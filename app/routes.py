"""
routes.py - WITH ULTRA-FAST BUILD OPTIONS
Added performance toggles and offline mode
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
cached_projects = {}


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
        info = SystemInfo().to_dict()
        # Add performance recommendations
        info['recommendations'] = {
            'parallel_builds': info['recommended_workers'],
            'maven_threads': info['recommended_maven_threads'],
            'jvm_memory_gb': info['recommended_jvm_memory'],
            'expected_speedup': f"{info['recommended_workers']}x faster (parallel)"
        }
        return jsonify(info)

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

        print(f"\n=== Loading projects for group: {group_id} ===")
        projects = gitlab_client.get_group_projects(group_id)
        cached_projects[group_id] = projects

        enriched = []
        for p in projects:
            default_branch = p.get('default_branch') or 'main'
            enriched.append({
                'id': p['id'],
                'name': p['name'],
                'http_url_to_repo': p['http_url_to_repo'],
                'default_branch': default_branch,
                'path_with_namespace': p['path_with_namespace'],
                'web_url': p['web_url']
            })
            print(f"  Project: {p['name']} | Default: {default_branch}")

        print(f"=== Total projects loaded: {len(enriched)} ===\n")
        return jsonify({
            'projects': enriched,
            'count': len(enriched)
        })

    @app.route('/api/project/<int:project_id>/branches')
    def get_project_branches(project_id):
        if not gitlab_client:
            return jsonify({'error': 'Not connected', 'branches': []}), 400

        print(f"\n=== Fetching ALL branches for project ID: {project_id} ===")

        try:
            branches = gitlab_client.get_project_branches(project_id)

            if not branches:
                print(f"⚠️ No branches returned from GitLab API")
                return jsonify({
                    'error': 'No branches found',
                    'project_id': project_id,
                    'branches': [],
                    'default_branch': 'main',
                    'count': 0
                }), 200

            default_branch = 'main'
            project_name = f"Project {project_id}"

            for projects in cached_projects.values():
                for p in projects:
                    if p['id'] == project_id:
                        default_branch = p.get('default_branch') or 'main'
                        project_name = p['name']
                        break

            print(f"  Project: {project_name}")
            print(f"  Default branch: {default_branch}")
            print(f"  Total branches: {len(branches)}")

            enriched = []
            for branch in branches:
                is_default = (branch == default_branch)
                enriched.append({
                    'name': branch,
                    'is_default': is_default,
                    'display': f"{branch}{'🌟' if is_default else ''}"
                })
                if is_default:
                    print(f"    ✓ {branch} (default)")

            enriched.sort(key=lambda x: (not x['is_default'], x['name'].lower()))

            print(f"=== Branches loaded successfully ===\n")

            return jsonify({
                'success': True,
                'project_id': project_id,
                'project_name': project_name,
                'branches': enriched,
                'branch_names': branches,
                'default_branch': default_branch,
                'count': len(branches)
            })

        except Exception as e:
            print(f"❌ ERROR loading branches: {str(e)}")
            import traceback
            traceback.print_exc()

            return jsonify({
                'error': str(e),
                'project_id': project_id,
                'branches': [],
                'default_branch': 'main',
                'count': 0
            }), 500

    @app.route('/api/build', methods=['POST'])
    def start_build():
        """
        Build services with ULTRA-FAST optimizations
        """
        data = request.json
        group_id = data.get('group_id')
        build_configs = data.get('build_configs', [])
        force = data.get('force', False)
        max_workers = int(data.get('max_workers', 4))

        # NEW: Performance options
        offline_mode = data.get('offline_mode', False)
        skip_tests = data.get('skip_tests', True)
        skip_javadoc = data.get('skip_javadoc', True)
        skip_source = data.get('skip_source', True)
        aggressive_parallel = data.get('aggressive_parallel', True)

        if not group_id or not build_configs:
            return jsonify({'error': 'Invalid request: Missing group_id or build_configs'}), 400

        settings = config_manager.load_group_settings(group_id)
        xml_path = config_manager.get_settings_xml_path(group_id)
        if not xml_path:
            return jsonify({'error': 'settings.xml not configured for this group'}), 400

        print(f"\n{'='*60}")
        print(f"ULTRA-FAST BUILD REQUEST")
        print(f"{'='*60}")
        print(f"Group ID: {group_id}")
        print(f"Services: {len(build_configs)}")
        print(f"Force rebuild: {force}")
        print(f"Max workers: {max_workers}")
        print(f"Offline mode: {offline_mode}")
        print(f"Skip tests: {skip_tests}")
        print(f"Skip javadoc: {skip_javadoc}")
        print(f"Skip source: {skip_source}")
        print(f"Aggressive parallel: {aggressive_parallel}")

        configs = []
        for idx, conf in enumerate(build_configs, 1):
            try:
                project_id = conf.get('project_id')
                service_name = conf.get('name')
                repo_url = conf.get('repo_url')
                selected_branch = conf.get('branch')
                default_branch = conf.get('default_branch', 'main')

                if not service_name or not repo_url:
                    continue

                if not selected_branch:
                    selected_branch = default_branch

                force_fetch = (selected_branch != default_branch)

                # Get Maven threads from settings or use system recommendation
                maven_threads = settings.get('maven_threads', SystemInfo().recommended_maven_threads)

                config = BuildConfig(
                    service_name=service_name,
                    group_id=group_id,
                    repo_url=repo_url,
                    branch=selected_branch,
                    settings_file=xml_path,
                    maven_profiles=settings.get('default_profiles', []),
                    jvm_options=settings.get('jvm_options', ''),
                    maven_threads=maven_threads,
                    force_full_fetch=force_fetch,
                    # NEW: Performance flags
                    skip_tests=skip_tests,
                    skip_javadoc=skip_javadoc,
                    skip_source=skip_source,
                    offline_mode=offline_mode,
                    aggressive_parallel=aggressive_parallel
                )
                configs.append(config)

            except Exception as e:
                print(f"❌ Error processing config {idx}: {e}")
                continue

        if not configs:
            return jsonify({'error': 'No valid build configurations'}), 400

        print(f"\n{'='*60}")
        print(f"VALIDATED: {len(configs)} services ready")
        print(f"Expected time reduction: {max_workers}x faster (parallel)")
        print(f"{'='*60}\n")

        builder.max_workers = max_workers

        def build_thread():
            try:
                results = builder.build_services(configs, force=force)
                success = sum(1 for r in results if r['status'] == 'success')
                skipped = sum(1 for r in results if r['status'] == 'skipped')
                failed = len(results) - success - skipped

                socketio.emit('build_complete', {
                    'success': success,
                    'failed': failed,
                    'skipped': skipped,
                    'total': len(results)
                })
            except Exception as e:
                print(f"❌ Build thread error: {e}")
                import traceback
                traceback.print_exc()
                socketio.emit('build_complete', {
                    'success': 0,
                    'failed': len(configs),
                    'skipped': 0,
                    'total': len(configs)
                })

        threading.Thread(target=build_thread, daemon=True).start()

        return jsonify({
            'success': True,
            'message': f'Started ULTRA-FAST build for {len(configs)} services',
            'services': [c.service_name for c in configs],
            'estimated_speedup': f"{max_workers}x"
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
        print("✅ Client connected")

    @socketio.on('disconnect')
    def on_disconnect():
        print("❌ Client disconnected")