"""
routes.py - FULLY FIXED FOR BRANCH SUPPORT
Now: ANY branch from GitLab API works!
No more "stuck on main"
"""

from flask import request, jsonify, render_template_string
import threading
from app.templates import HTML_TEMPLATE
from app.services.gitlab_client import GitLabClient
from app.services.builder import BuildConfig
from app.utils.system_info import SystemInfo

# Global state
gitlab_client = None
cached_groups = []
cached_projects = {}  # {group_id: [projects]}


def register_routes(app, socketio, config_manager, builder):
    global gitlab_client, cached_groups, cached_projects

    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/config')
    def get_config():
        config = config_manager.load_gitlab_config()
        return jsonify({
            'gitlab_url': config.get('gitlab_url', 'https://gitlab.com'),
            'maven_path': config.get('maven_path', '')
        })

    @app.route('/api/system-info')
    def get_system_info():
        return jsonify(SystemInfo().to_dict())

    @app.route('/api/prerequisites')
    def check_prerequisites():
        return jsonify(builder.check_prerequisites())

    @app.route('/api/set-maven-path', methods=['POST'])
    def set_maven_path():
        data = request.json
        path = data.get('maven_path', '').strip()
        if not path:
            return jsonify({'success': False, 'error': 'Path required'}), 400

        from app.services.command_finder import CommandFinder
        info = CommandFinder().verify_maven(path)
        if not info['available']:
            return jsonify({'success': False, 'error': 'Maven not working'}), 400

        config = config_manager.load_gitlab_config()
        config['maven_path'] = path
        config_manager.save_gitlab_config(config)
        builder.maven_cmd = path

        return jsonify({
            'success': True,
            'version': info['version'],
            'message': 'Maven path saved'
        })

    @app.route('/api/connect', methods=['POST'])
    def connect_gitlab():
        global gitlab_client, cached_groups
        data = request.json
        url = data.get('gitlab_url')
        token = data.get('private_token')

        if not url or not token:
            return jsonify({'success': False, 'error': 'Missing credentials'}), 400

        config_manager.save_gitlab_config({'gitlab_url': url, 'private_token': token})
        gitlab_client = GitLabClient(url, token)
        cached_groups = gitlab_client.get_groups()

        return jsonify({'success': True, 'groups': cached_groups})

    @app.route('/api/projects/<group_id>')
    def get_projects(group_id):
        global cached_projects
        if not gitlab_client:
            return jsonify({'error': 'Not connected'}), 400

        projects = gitlab_client.get_group_projects(group_id)
        cached_projects[group_id] = projects

        enriched = []
        for p in projects:
            enriched.append({
                'id': p['id'],
                'name': p['name'],
                'http_url_to_repo': p['http_url_to_repo'],
                'default_branch': p.get('default_branch') or 'main',
                'path_with_namespace': p['path_with_namespace'],
                'web_url': p['web_url']
            })

        return jsonify({
            'projects': enriched,
            'count': len(enriched)
        })

    @app.route('/api/project/<int:project_id>/branches')
    def get_project_branches(project_id):
        if not gitlab_client:
            return jsonify({'error': 'Not connected'}), 400

        try:
            branches = gitlab_client.get_project_branches(project_id)
            default = 'main'

            # Find default branch from cache
            for projects in cached_projects.values():
                for p in projects:
                    if p['id'] == project_id:
                        default = p.get('default_branch') or 'main'
                        break

            # Mark default with star
            enriched = []
            for b in branches:
                enriched.append({
                    'name': b,
                    'is_default': b == default,
                    'display': f"{b} (default)" if b == default else b
                })

            return jsonify({
                'project_id': project_id,
                'branches': enriched,
                'default_branch': default,
                'count': len(branches)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/build', methods=['POST'])
    def start_build():
        """
        FIXED: Now supports ANY branch from GitLab
        """
        data = request.json
        group_id = data.get('group_id')
        build_configs = data.get('build_configs', [])
        force = data.get('force', False)
        max_workers = int(data.get('max_workers', 4))

        if not group_id or not build_configs:
            return jsonify({'error': 'Invalid request'}), 400

        settings = config_manager.load_group_settings(group_id)
        xml_path = config_manager.get_settings_xml_path(group_id)
        if not xml_path:
            return jsonify({'error': 'settings.xml not configured'}), 400

        configs = []
        for conf in build_configs:
            project_id = conf['project_id']
            selected_branch = conf['branch']

            # Find default branch
            default_branch = 'main'
            for p in cached_projects.get(group_id, []):
                if p['id'] == project_id:
                    default_branch = p.get('default_branch') or 'main'
                    break

            # CRITICAL: Force full fetch if not default
            force_fetch = (selected_branch != default_branch)

            config = BuildConfig(
                service_name=conf['name'],
                group_id=group_id,
                repo_url=conf['repo_url'],
                branch=selected_branch,
                settings_file=xml_path,
                maven_profiles=settings.get('default_profiles', []),
                jvm_options=settings.get('jvm_options', ''),
                maven_threads=settings.get('maven_threads', 4),
                force_full_fetch=force_fetch   # NEW FLAG
            )
            configs.append(config)

        builder.max_workers = max_workers

        def build_thread():
            results = builder.build_services(configs, force=force)
            success = sum(1 for r in results if r['status'] == 'success')
            failed = len(results) - success
            socketio.emit('build_complete', {
                'success': success,
                'failed': failed,
                'total': len(results)
            })

        threading.Thread(target=build_thread, daemon=True).start()
        return jsonify({
            'message': f'Started build for {len(configs)} services',
            'services': [c.service_name for c in configs]
        })

    @app.route('/api/settings-files')
    def list_settings_files():
        return jsonify({'files': config_manager.list_settings_files()})

    @app.route('/api/group/settings/<group_id>')
    def get_group_settings(group_id):
        settings = config_manager.load_group_settings(group_id)
        xml_path = config_manager.get_settings_xml_path(group_id)
        return jsonify({
            'configured': bool(xml_path),
            'settings': {
                'settings_xml_path': xml_path or '',
                'jvm_options': settings.get('jvm_options', ''),
                'default_profiles': settings.get('default_profiles', []),
                'maven_threads': settings.get('maven_threads', 4)
            }
        })

    @app.route('/api/group/settings', methods=['POST'])
    def save_group_settings():
        data = request.json
        group_id = data.get('group_id')
        file_name = data.get('settings_file_name')
        content = data.get('settings_xml_content')

        if not group_id:
            return jsonify({'error': 'Group ID required'}), 400

        if file_name:
            xml_path = config_manager.get_settings_file_path(file_name)
        elif content:
            xml_path = config_manager.save_settings_xml(group_id, content)
        else:
            return jsonify({'error': 'No file provided'}), 400

        if not xml_path:
            return jsonify({'error': 'Save failed'}), 400

        settings = {
            'settings_xml_path': xml_path,
            'jvm_options': data.get('jvm_options', ''),
            'default_profiles': data.get('maven_profiles', []),
            'maven_threads': data.get('maven_threads', 4)
        }
        config_manager.save_group_settings(group_id, settings)

        return jsonify({
            'message': 'Settings saved!',
            'path': xml_path
        })

    @app.route('/api/cache/clear', methods=['POST'])
    def clear_cache():
        builder.build_cache.clear()
        return jsonify({'message': 'Cache cleared'})

    @app.route('/api/cache/info')
    def get_cache_info():
        data = [
            {
                'service': k,
                'branch': v.get('branch', ''),
                'commit': v.get('commit', '')[:8],
                'time': v.get('timestamp', '')
            }
            for k, v in builder.build_cache.cache.items()
        ]
        return jsonify({'cache': data, 'count': len(data)})

    @socketio.on('connect')
    def on_connect():
        print("Client connected")

    @socketio.on('disconnect')
    def on_disconnect():
        print("Client disconnected")