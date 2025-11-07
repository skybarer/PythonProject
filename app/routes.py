"""
Application routes and API endpoints - SEQUENTIAL FLOW VERSION
Key changes:
1. Load projects first (shows microservices list)
2. Separate API to fetch branches for each project
3. Build uses selected branches per service
"""

from flask import request, jsonify, render_template_string
import threading
from app.templates import HTML_TEMPLATE
from app.services.gitlab_client import GitLabClient
from app.services.builder import BuildConfig
from app.utils.system_info import SystemInfo

# Global variables
gitlab_client = None
cached_groups = []
cached_projects = {}


def register_routes(app, socketio, config_manager, builder):
    """Register all application routes"""

    global gitlab_client, cached_groups, cached_projects

    @app.route('/')
    def index():
        """Main page"""
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/config')
    def get_config():
        """Get saved configuration"""
        config = config_manager.load_gitlab_config()
        return jsonify({
            'gitlab_url': config.get('gitlab_url', 'https://gitlab.com')
        })

    @app.route('/api/system-info')
    def get_system_info():
        """Get system information"""
        sys_info = SystemInfo()
        return jsonify(sys_info.to_dict())

    @app.route('/api/prerequisites')
    def check_prerequisites():
        """Check if Git and Maven are available"""
        prereqs = builder.check_prerequisites()
        return jsonify(prereqs)

    @app.route('/api/set-maven-path', methods=['POST'])
    def set_maven_path():
        """Set custom Maven path"""
        data = request.json
        maven_path = data.get('maven_path', '').strip()

        if not maven_path:
            return jsonify({'success': False, 'error': 'Maven path required'}), 400

        # Verify the Maven path works
        from app.services.command_finder import CommandFinder
        finder = CommandFinder()
        maven_info = finder.verify_maven(maven_path)

        if maven_info['available']:
            # Save to config
            config = config_manager.load_gitlab_config()
            config['maven_path'] = maven_path
            config_manager.save_gitlab_config(config)

            # Update builder's Maven command
            builder.maven_cmd = maven_path

            return jsonify({
                'success': True,
                'message': 'Maven path set successfully',
                'version': maven_info['version']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid Maven path or Maven not working'
            }), 400

    @app.route('/api/connect', methods=['POST'])
    def connect_gitlab():
        """Connect to GitLab"""
        global gitlab_client, cached_groups

        data = request.json
        gitlab_url = data.get('gitlab_url')
        private_token = data.get('private_token')

        if not gitlab_url or not private_token:
            return jsonify({'success': False, 'error': 'Missing credentials'}), 400

        # Save configuration
        config = {
            'gitlab_url': gitlab_url,
            'private_token': private_token
        }
        config_manager.save_gitlab_config(config)

        # Create GitLab client
        gitlab_client = GitLabClient(gitlab_url, private_token)
        cached_groups = gitlab_client.get_groups()

        return jsonify({
            'success': True,
            'groups': cached_groups
        })

    @app.route('/api/projects/<group_id>')
    def get_projects(group_id):
        """
        Step 1: Get projects in a group (shows microservices list)
        Returns basic project info with default branch only
        """
        global cached_projects

        if not gitlab_client:
            return jsonify({'error': 'Not connected to GitLab'}), 400

        projects = gitlab_client.get_group_projects(group_id)

        # Store in cache
        cached_projects[group_id] = projects

        # Return simplified project list
        project_list = []
        for project in projects:
            project_list.append({
                'id': project['id'],
                'name': project['name'],
                'http_url_to_repo': project['http_url_to_repo'],
                'default_branch': project.get('default_branch', 'master'),
                'description': project.get('description', ''),
                'path_with_namespace': project.get('path_with_namespace', '')
            })

        return jsonify({
            'projects': project_list,
            'count': len(project_list)
        })

    @app.route('/api/project/<int:project_id>/branches')
    def get_project_branches(project_id):
        """
        Step 2: Get all branches for a specific project
        Called on-demand when user selects a service
        """
        if not gitlab_client:
            return jsonify({'error': 'Not connected to GitLab'}), 400

        try:
            branches = gitlab_client.get_project_branches(project_id)
            return jsonify({
                'project_id': project_id,
                'branches': branches,
                'count': len(branches)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/projects/<group_id>/branches-bulk', methods=['POST'])
    def get_branches_bulk(group_id):
        """
        Optional: Get branches for multiple projects at once
        Accepts list of project IDs
        """
        if not gitlab_client:
            return jsonify({'error': 'Not connected to GitLab'}), 400

        data = request.json
        project_ids = data.get('project_ids', [])

        if not project_ids:
            return jsonify({'error': 'No project IDs provided'}), 400

        results = {}
        for project_id in project_ids:
            try:
                branches = gitlab_client.get_project_branches(project_id)
                results[str(project_id)] = branches
            except Exception as e:
                results[str(project_id)] = {'error': str(e)}

        return jsonify({
            'results': results,
            'count': len(results)
        })

    @app.route('/api/settings-files')
    def list_settings_files():
        """List available settings.xml files"""
        files = config_manager.list_settings_files()
        return jsonify({'files': files})

    @app.route('/api/group/settings/<group_id>')
    def get_group_settings(group_id):
        """Get settings for a specific group"""
        settings = config_manager.load_group_settings(group_id)
        settings_xml_path = config_manager.get_settings_xml_path(group_id)

        return jsonify({
            'configured': bool(settings_xml_path),
            'settings': {
                'settings_xml_path': settings_xml_path,
                'jvm_options': settings.get('jvm_options', ''),
                'default_profiles': settings.get('default_profiles', []),
                'maven_threads': settings.get('maven_threads', 4)
            }
        })

    @app.route('/api/group/settings', methods=['POST'])
    def save_group_settings():
        """Save group settings including settings.xml file"""
        data = request.json
        group_id = data.get('group_id')
        settings_file_name = data.get('settings_file_name')
        settings_xml_content = data.get('settings_xml_content')
        jvm_options = data.get('jvm_options', '')
        maven_profiles = data.get('maven_profiles', [])
        maven_threads = data.get('maven_threads', 4)

        if not group_id:
            return jsonify({'error': 'Group ID is required'}), 400

        # Handle settings file
        if settings_file_name:
            # Use existing file from dropdown
            settings_xml_path = config_manager.get_settings_file_path(settings_file_name)
        elif settings_xml_content:
            # Upload new file
            settings_xml_path = config_manager.save_settings_xml(group_id, settings_xml_content)
        else:
            return jsonify({'error': 'Settings file is required'}), 400

        if not settings_xml_path:
            return jsonify({'error': 'Failed to get settings file path'}), 400

        # Save other settings
        settings = {
            'settings_xml_path': settings_xml_path,
            'jvm_options': jvm_options,
            'default_profiles': maven_profiles,
            'maven_threads': maven_threads
        }

        config_manager.save_group_settings(group_id, settings)

        return jsonify({
            'message': 'Settings saved successfully',
            'settings_path': settings_xml_path
        })

    @app.route('/api/build', methods=['POST'])
    def start_build():
        """
        Step 3: Start build process with selected branches
        Expects build_configs with service name, repo_url, and branch
        """
        data = request.json
        group_id = data.get('group_id')
        build_configs = data.get('build_configs', [])
        force = data.get('force', False)
        max_workers = data.get('max_workers', 4)

        if not group_id:
            return jsonify({'error': 'Group ID is required'}), 400

        if not build_configs:
            return jsonify({'error': 'No services selected'}), 400

        # Load group settings
        settings = config_manager.load_group_settings(group_id)
        settings_xml_path = config_manager.get_settings_xml_path(group_id)

        if not settings_xml_path:
            return jsonify({'error': 'Group settings not configured. Please upload settings.xml first.'}), 400

        # Create BuildConfig objects from the provided configs
        configs = []
        for build_conf in build_configs:
            config = BuildConfig(
                service_name=build_conf['name'],
                group_id=group_id,
                repo_url=build_conf['repo_url'],
                branch=build_conf['branch'],
                settings_file=settings_xml_path,
                maven_profiles=settings.get('default_profiles', []),
                jvm_options=settings.get('jvm_options', ''),
                maven_threads=settings.get('maven_threads', 4)
            )
            configs.append(config)

        if not configs:
            return jsonify({'error': 'No valid services found'}), 400

        # Update builder max workers
        builder.max_workers = max_workers

        def build_thread():
            """Background build thread"""
            results = builder.build_services(configs, force=force)

            success = sum(1 for r in results if r['status'] == 'success')
            failed = sum(1 for r in results if r['status'] == 'failed')
            skipped = sum(1 for r in results if r['status'] == 'skipped')

            socketio.emit('build_complete', {
                'success': success,
                'failed': failed,
                'skipped': skipped
            })

        # Start build in background thread
        threading.Thread(target=build_thread, daemon=True).start()

        return jsonify({
            'message': f'Building {len(configs)} services...',
            'services': [c.service_name for c in configs]
        })

    @app.route('/api/cache/clear', methods=['POST'])
    def clear_cache():
        """Clear build cache"""
        builder.build_cache.clear()
        return jsonify({'message': 'Build cache cleared successfully'})

    @app.route('/api/logs/current', methods=['GET'])
    def get_current_logs():
        """Get current logs (if log buffer is implemented)"""
        return jsonify({'logs': 'Log export not yet implemented'})

    # SocketIO events
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print('Client disconnected')