# Routes Implementation Guide

Create `app/routes.py` with the following structure. This combines all routes from the original file with new enhancements.

## Required Routes

### 1. Main Route
```python
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)  # Import from templates.py
```

### 2. System Info Routes

```python
@app.route('/api/system-info')
def get_system_info():
    from build_automation.app import SystemInfo
    sys_info = SystemInfo()
    return jsonify(sys_info.to_dict())


@app.route('/api/prerequisites')
def check_prerequisites():
    prereqs = builder.check_prerequisites()
    return jsonify(prereqs)


@app.route('/api/set-maven-path', methods=['POST'])
def set_maven_path():
    data = request.json
    maven_path = data.get('maven_path', '').strip()

    if not maven_path:
        return jsonify({'success': False, 'error': 'Maven path required'}), 400

    # Verify and save
    from build_automation.app.services.command_finder import CommandFinder
    finder = CommandFinder()
    maven_info = finder.verify_maven(maven_path)

    if maven_info['available']:
        config = config_manager.load_gitlab_config()
        config['maven_path'] = maven_path
        config_manager.save_gitlab_config(config)
        builder.maven_cmd = maven_path
        return jsonify({'success': True, 'message': 'Maven path set'})
    else:
        return jsonify({'success': False, 'error': 'Invalid Maven path'}), 400
```

### 3. GitLab Routes

```python
@app.route('/api/connect', methods=['POST'])
def connect_gitlab():
    global gitlab_client, cached_groups
    data = request.json

    gitlab_url = data.get('gitlab_url')
    private_token = data.get('private_token')

    if not gitlab_url or not private_token:
        return jsonify({'success': False, 'error': 'Missing credentials'}), 400

    config_manager.save_gitlab_config({
        'gitlab_url': gitlab_url,
        'private_token': private_token
    })

    from build_automation.app.services import GitLabClient
    gitlab_client = GitLabClient(gitlab_url, private_token)
    cached_groups = gitlab_client.get_groups()

    return jsonify({'success': True, 'groups': cached_groups})


@app.route('/api/projects/<group_id>')
def get_projects(group_id):
    if not gitlab_client:
        return jsonify({'error': 'Not connected'}), 400

    projects = gitlab_client.get_group_projects(group_id)
    cached_projects[group_id] = projects
    return jsonify({'projects': projects})


@app.route('/api/project/<int:project_id>/branches')
def get_project_branches(project_id):
    if not gitlab_client:
        return jsonify({'error': 'Not connected'}), 400

    branches = gitlab_client.get_project_branches(project_id)
    return jsonify({'branches': branches})
```

### 4. Settings Routes
```python
@app.route('/api/settings-files')
def list_settings_files():
    files = config_manager.list_settings_files()
    return jsonify({'files': files})

@app.route('/api/group/settings/<group_id>')
def get_group_settings(group_id):
    settings = config_manager.load_group_settings(group_id)
    settings_xml_path = config_manager.get_settings_xml_path(group_id)
    
    return jsonify({
        'configured': bool(settings_xml_path),
        'settings': settings
    })

@app.route('/api/group/settings', methods=['POST'])
def save_group_settings():
    data = request.json
    group_id = data.get('group_id')
    settings_file_name = data.get('settings_file_name')  # NEW
    settings_xml_content = data.get('settings_xml_content')
    jvm_options = data.get('jvm_options', '')
    maven_profiles = data.get('maven_profiles', [])
    maven_threads = data.get('maven_threads', 4)  # NEW
    
    if not group_id:
        return jsonify({'error': 'Group ID required'}), 400
    
    # Handle settings file
    if settings_file_name:
        # Use existing file from dropdown
        settings_xml_path = config_manager.get_settings_file_path(settings_file_name)
    elif settings_xml_content:
        # Upload new file
        settings_xml_path = config_manager.save_settings_xml(group_id, settings_xml_content)
    else:
        return jsonify({'error': 'Settings file required'}), 400
    
    # Save group settings
    settings = {
        'settings_xml_path': settings_xml_path,
        'jvm_options': jvm_options,
        'default_profiles': maven_profiles,
        'maven_threads': maven_threads
    }
    
    config_manager.save_group_settings(group_id, settings)
    return jsonify({'message': 'Settings saved', 'path': settings_xml_path})
```

### 5. Build Routes

```python
@app.route('/api/build', methods=['POST'])
def start_build():
    data = request.json
    group_id = data.get('group_id')
    build_configs = data.get('build_configs', [])  # NEW: includes branch per service
    force = data.get('force', False)
    max_workers = data.get('max_workers', 4)

    if not group_id or not build_configs:
        return jsonify({'error': 'Invalid request'}), 400

    # Load group settings
    settings = config_manager.load_group_settings(group_id)
    settings_xml_path = config_manager.get_settings_xml_path(group_id)

    if not settings_xml_path:
        return jsonify({'error': 'Group settings not configured'}), 400

    # Create BuildConfig objects
    from build_automation.app.services import BuildConfig
    configs = []

    for build_conf in build_configs:
        config = BuildConfig(
            service_name=build_conf['name'],
            group_id=group_id,
            repo_url=build_conf['repo_url'],
            branch=build_conf.get('branch', 'master'),  # NEW
            settings_file=settings_xml_path,
            maven_profiles=settings.get('default_profiles', []),
            jvm_options=settings.get('jvm_options', ''),
            maven_threads=settings.get('maven_threads', 4)
        )
        configs.append(config)

    builder.max_workers = max_workers

    def build_thread():
        results = builder.build_services(configs, force=force)

        success = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'failed')
        skipped = sum(1 for r in results if r['status'] == 'skipped')

        socketio.emit('build_complete', {
            'success': success,
            'failed': failed,
            'skipped': skipped
        })

    import threading
    threading.Thread(target=build_thread, daemon=True).start()

    return jsonify({'message': f'Building {len(configs)} services...'})


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    builder.build_cache.clear()
    return jsonify({'message': 'Cache cleared'})
```

### 6. NEW: Logs Export Route
```python
@app.route('/api/logs/current', methods=['GET'])
def get_current_logs():
    # Return current log buffer (implement log storage in builder)
    return jsonify({'logs': builder.get_log_buffer()})
```

## Complete Function to Register All Routes

```python
# app/routes.py
from flask import request, jsonify, render_template_string
from build_automation.app import HTML_TEMPLATE

# Global variables
gitlab_client = None
cached_groups = []
cached_projects = {}


def register_routes(app, socketio, config_manager, builder):
    """Register all application routes"""

    # Import here to avoid circular imports
    global gitlab_client, cached_groups, cached_projects

    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)

    # ... add all routes above here ...

    # SocketIO events
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
```

## Integration in `app/__init__.py`

```python
from build_automation.app import register_routes


def create_app():
    # ... app initialization ...

    register_routes(app, socketio, config_manager, builder)

    return app, socketio
```

This structure keeps routes organized and maintainable while adding all the new features.