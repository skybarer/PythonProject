"""
Enhanced UI templates with:
1. Per-service branch selection
2. Fixed button loading states
3. Better UX for multi-branch builds
"""

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Microservice Build Automation</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .content { padding: 30px; }
        .section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .section h2 {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #333;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-right: 10px;
            margin-bottom: 10px;
            position: relative;
            display: inline-block;
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover:not(:disabled) { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); 
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover:not(:disabled) { background: #5a6268; }
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        .btn-danger:hover:not(:disabled) { background: #c82333; }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover:not(:disabled) { background: #218838; }
        .btn-info {
            background: #17a2b8;
            color: white;
        }
        .btn-info:hover:not(:disabled) { background: #138496; }

        /* Loading spinner - FIXED */
        .btn.loading {
            pointer-events: none;
        }
        .btn.loading::after {
            content: "";
            position: absolute;
            width: 16px;
            height: 16px;
            top: 50%;
            right: 10px;
            margin-top: -8px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.6s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        #servicesList {
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 10px;
            max-height: 400px;
            overflow-y: auto;
            background: white;
        }
        .service-item {
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 2px solid transparent;
        }
        .service-item:hover { 
            background: #e9ecef; 
            border-color: #dee2e6;
        }
        .service-item.selected {
            background: #667eea;
            color: white;
            border-color: #5568d3;
        }
        .service-name {
            font-weight: 500;
            flex: 1;
        }
        .branch-selector {
            margin-left: 10px;
            padding: 4px 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 12px;
            background: white;
            color: #333;
            min-width: 120px;
        }
        .service-item.selected .branch-selector {
            border-color: #fff;
            background: #fff;
        }
        #logOutput {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 6px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .status-bar {
            background: #f8f9fa;
            padding: 15px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            font-weight: 600;
            color: #666;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin-right: 8px;
        }
        .file-upload-area {
            border: 2px dashed #ddd;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: white;
        }
        .file-upload-area:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        .file-upload-area.dragover {
            border-color: #667eea;
            background: #f0f3ff;
        }
        .file-info {
            margin-top: 10px;
            padding: 10px;
            background: #e7f3ff;
            border-radius: 4px;
            font-size: 13px;
        }
        .settings-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
        .settings-status.configured {
            background: #d4edda;
            color: #155724;
        }
        .settings-status.not-configured {
            background: #f8d7da;
            color: #721c24;
        }
        .group-info {
            font-size: 13px;
            color: #666;
            margin-top: 5px;
        }
        .prereq-status {
            background: white;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
            font-size: 13px;
        }
        .prereq-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        .prereq-item:last-child {
            border-bottom: none;
        }
        .prereq-ok {
            color: #28a745;
            font-weight: 600;
        }
        .prereq-error {
            color: #dc3545;
            font-weight: 600;
        }
        .branch-info {
            font-size: 11px;
            color: #999;
            margin-top: 5px;
        }
        .service-item.selected .branch-info {
            color: rgba(255,255,255,0.8);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Microservice Build Automation</h1>
            <p>Parallel builds with per-service branch selection and intelligent caching</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>System Prerequisites</h2>
                <button class="btn btn-info" id="btnCheckPrereq" onclick="checkPrerequisites()">Check Git & Maven</button>
                <div id="prereqStatus" class="prereq-status" style="display: none;"></div>

                <div style="margin-top: 15px;">
                    <h3 style="font-size: 1.1em; margin-bottom: 10px;">Manual Configuration (if not detected)</h3>
                    <div class="form-group">
                        <label>Maven Path (optional - e.g., C:\path\to\apache-maven-3.9.9\bin\mvn.cmd)</label>
                        <input type="text" id="mavenPath" placeholder="Leave empty for auto-detection">
                    </div>
                    <button class="btn btn-success" id="btnSetMaven" onclick="setMavenPath()">Set Maven Path</button>
                </div>
            </div>

            <div class="section">
                <h2>GitLab Configuration</h2>
                <div class="form-group">
                    <label>GitLab URL</label>
                    <input type="text" id="gitlabUrl" placeholder="https://gitlab.com" value="https://gitlab.com">
                </div>
                <div class="form-group">
                    <label>Private Token</label>
                    <input type="password" id="privateToken" placeholder="Enter your GitLab private token">
                </div>
                <button class="btn btn-primary" id="btnConnect" onclick="connectGitLab()">Connect to GitLab</button>
            </div>

            <div class="section">
                <h2>Group Configuration</h2>
                <div class="form-group">
                    <label>Group <span id="settingsStatus" class="settings-status not-configured">Not Configured</span></label>
                    <select id="groupSelect" onchange="checkGroupSettings()">
                        <option value="">-- Select a group --</option>
                    </select>
                    <div class="group-info" id="groupInfo"></div>
                </div>

                <div class="form-group">
                    <label>Maven Settings File (settings.xml)</label>
                    <div class="file-upload-area" id="fileUploadArea" onclick="document.getElementById('settingsFile').click()">
                        <div>📁 Click or drag to upload settings.xml</div>
                        <input type="file" id="settingsFile" accept=".xml" style="display: none;" onchange="handleFileSelect(event)">
                    </div>
                    <div id="fileInfo" class="file-info" style="display: none;"></div>
                </div>

                <div class="form-group">
                    <label>JVM Options</label>
                    <input type="text" id="jvmOptions" placeholder="-Xmx2G -XX:+UseParallelGC" value="-Xmx2G -XX:+UseParallelGC">
                </div>

                <div class="form-group">
                    <label>Maven Profiles (comma-separated)</label>
                    <input type="text" id="mavenProfiles" placeholder="e.g., prod,security">
                </div>

                <button class="btn btn-success" id="btnSaveSettings" onclick="saveGroupSettings()">Save Group Settings</button>
                <button class="btn btn-secondary" id="btnLoadProjects" onclick="loadProjects()">Load Projects</button>
            </div>

            <div class="section">
                <h2>Build Services</h2>
                <div class="form-group">
                    <label>Services (Click to select, choose branch for each)</label>
                    <div id="servicesList"></div>
                </div>
                <div class="checkbox-group">
                    <input type="checkbox" id="forceRebuild">
                    <label for="forceRebuild" style="margin-bottom: 0;">Force rebuild (ignore cache)</label>
                </div>
                <div class="form-group">
                    <label>Parallel Builds</label>
                    <input type="number" id="maxWorkers" value="4" min="1" max="16">
                </div>
                <button class="btn btn-primary" id="btnBuildSelected" onclick="buildSelected()">Build Selected</button>
                <button class="btn btn-secondary" id="btnBuildAll" onclick="buildAll()">Build All</button>
                <button class="btn btn-danger" id="btnClearCache" onclick="clearCache()">Clear Cache</button>
                <button class="btn btn-info" id="btnClearLogs" onclick="clearLogs()">Clear Logs</button>
            </div>

            <div class="section">
                <h2>Build Log</h2>
                <div id="logOutput"></div>
            </div>
        </div>

        <div class="status-bar" id="statusBar">Ready</div>
    </div>

    <script>
        const socket = io();
        let selectedServices = new Map(); // Changed to Map to store {name, branch, repo_url}
        let settingsFileContent = null;
        let currentProjects = []; // Store loaded projects

        socket.on('log', function(data) {
            const logOutput = document.getElementById('logOutput');
            const message = data.message.replace(/\n/g, '<br>');
            logOutput.innerHTML += message + '<br>';
            logOutput.scrollTop = logOutput.scrollHeight;
        });

        socket.on('build_complete', function(data) {
            const status = `Build Complete - Success: ${data.success}, Failed: ${data.failed}, Skipped: ${data.skipped}`;
            updateStatus(status);

            // Re-enable build buttons - FIXED
            enableBuildButtons();

            // Show summary in logs
            const logOutput = document.getElementById('logOutput');
            logOutput.innerHTML += '<br><span style="color: #4CAF50; font-weight: bold;">========================================</span><br>';
            logOutput.innerHTML += '<span style="color: #4CAF50; font-weight: bold;">BUILD SUMMARY</span><br>';
            logOutput.innerHTML += '<span style="color: #4CAF50; font-weight: bold;">========================================</span><br>';
            logOutput.innerHTML += `<span style="color: #4CAF50;">✅ Success: ${data.success}</span><br>`;
            logOutput.innerHTML += `<span style="color: #f44336;">❌ Failed: ${data.failed}</span><br>`;
            logOutput.innerHTML += `<span style="color: #FF9800;">⏭️ Skipped: ${data.skipped}</span><br>`;
            logOutput.innerHTML += '<span style="color: #4CAF50; font-weight: bold;">========================================</span><br>';
            logOutput.scrollTop = logOutput.scrollHeight;
        });

        // Button loading helpers - FIXED
        function setButtonLoading(buttonId, loading, text = 'Loading...') {
            const btn = document.getElementById(buttonId);
            if (!btn) return;

            if (loading) {
                btn.disabled = true;
                btn.classList.add('loading');
                if (!btn.dataset.originalText) {
                    btn.dataset.originalText = btn.textContent;
                }
                btn.textContent = text;
            } else {
                btn.disabled = false;
                btn.classList.remove('loading');
                if (btn.dataset.originalText) {
                    btn.textContent = btn.dataset.originalText;
                    delete btn.dataset.originalText;
                }
            }
        }

        function disableBuildButtons() {
            setButtonLoading('btnBuildSelected', true, 'Building...');
            setButtonLoading('btnBuildAll', true, 'Building...');
        }

        function enableBuildButtons() {
            setButtonLoading('btnBuildSelected', false);
            setButtonLoading('btnBuildAll', false);
        }

        // File upload handling
        const fileUploadArea = document.getElementById('fileUploadArea');

        fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadArea.classList.add('dragover');
        });

        fileUploadArea.addEventListener('dragleave', () => {
            fileUploadArea.classList.remove('dragover');
        });

        fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.name.endsWith('.xml')) {
                readSettingsFile(file);
            } else {
                alert('Please upload a valid XML file');
            }
        });

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                readSettingsFile(file);
            }
        }

        function readSettingsFile(file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                settingsFileContent = e.target.result;
                document.getElementById('fileInfo').style.display = 'block';
                document.getElementById('fileInfo').innerHTML = `✓ File loaded: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
            };
            reader.readAsText(file);
        }

        async function checkPrerequisites() {
            setButtonLoading('btnCheckPrereq', true);
            updateStatus('Checking prerequisites...');
            const prereqStatus = document.getElementById('prereqStatus');

            try {
                const response = await fetch('/api/prerequisites');
                const data = await response.json();

                let html = '<h3 style="margin-bottom: 10px;">System Check Results:</h3>';

                // Git status
                const gitClass = data.git.available ? 'prereq-ok' : 'prereq-error';
                html += `<div class="prereq-item">
                    <span><strong>Git:</strong> ${data.git.version}</span>
                    <span class="${gitClass}">${data.git.available ? '✓ Available' : '✗ Not Found'}</span>
                </div>`;
                if (data.git.path) {
                    html += `<div style="font-size: 12px; color: #666; padding: 5px 0;">Path: ${data.git.path}</div>`;
                }

                // Maven status
                const mavenClass = data.maven.available ? 'prereq-ok' : 'prereq-error';
                html += `<div class="prereq-item">
                    <span><strong>Maven:</strong> ${data.maven.version}</span>
                    <span class="${mavenClass}">${data.maven.available ? '✓ Available' : '✗ Not Found'}</span>
                </div>`;
                if (data.maven.path) {
                    html += `<div style="font-size: 12px; color: #666; padding: 5px 0;">Path: ${data.maven.path}</div>`;
                } else {
                    html += `<div style="font-size: 12px; color: #dc3545; padding: 5px 0;">
                        ⚠️ Maven not found. Please set the path manually below or add Maven to your system PATH.
                        <br>Example: C:\\\\Users\\\\YourName\\\\Documents\\\\software\\\\apache-maven-3.9.9\\\\bin\\\\mvn.cmd
                    </div>`;
                }

                prereqStatus.innerHTML = html;
                prereqStatus.style.display = 'block';

                if (!data.git.available || !data.maven.available) {
                    updateStatus('⚠️ Prerequisites not met - check system requirements');
                } else {
                    updateStatus('✓ All prerequisites satisfied');
                }
            } catch (error) {
                alert('Error checking prerequisites: ' + error);
                updateStatus('Error checking prerequisites');
            } finally {
                setButtonLoading('btnCheckPrereq', false);
            }
        }

        async function setMavenPath() {
            const mavenPath = document.getElementById('mavenPath').value.trim();

            if (!mavenPath) {
                alert('Please enter a Maven path');
                return;
            }

            setButtonLoading('btnSetMaven', true);

            try {
                const response = await fetch('/api/set-maven-path', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({maven_path: mavenPath})
                });

                const data = await response.json();

                if (data.success) {
                    alert('Maven path set successfully! Click "Check Git & Maven" to verify.');
                    await checkPrerequisites();
                } else {
                    alert('Failed to set Maven path: ' + data.error);
                }
            } catch (error) {
                alert('Error setting Maven path: ' + error);
            } finally {
                setButtonLoading('btnSetMaven', false);
            }
        }

        async function connectGitLab() {
            const url = document.getElementById('gitlabUrl').value;
            const token = document.getElementById('privateToken').value;

            if (!url || !token) {
                alert('Please enter GitLab URL and token');
                return;
            }

            setButtonLoading('btnConnect', true, 'Connecting...');
            updateStatus('Connecting to GitLab...');

            try {
                const response = await fetch('/api/connect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({gitlab_url: url, private_token: token})
                });

                const data = await response.json();

                if (data.success) {
                    const groupSelect = document.getElementById('groupSelect');
                    groupSelect.innerHTML = '<option value="">-- Select a group --</option>';
                    data.groups.forEach(group => {
                        const option = document.createElement('option');
                        option.value = group.id;
                        option.textContent = `${group.full_path} (${group.name})`;
                        groupSelect.appendChild(option);
                    });
                    updateStatus(`Connected! Loaded ${data.groups.length} groups`);
                } else {
                    alert('Failed to connect: ' + data.error);
                    updateStatus('Connection failed');
                }
            } catch (error) {
                alert('Error connecting to GitLab: ' + error);
                updateStatus('Connection error');
            } finally {
                setButtonLoading('btnConnect', false);
            }
        }

        async function checkGroupSettings() {
            const groupId = document.getElementById('groupSelect').value;
            if (!groupId) {
                document.getElementById('settingsStatus').className = 'settings-status not-configured';
                document.getElementById('settingsStatus').textContent = 'Not Configured';
                document.getElementById('groupInfo').textContent = '';
                return;
            }

            try {
                const response = await fetch(`/api/group/settings/${groupId}`);
                const data = await response.json();

                if (data.configured) {
                    document.getElementById('settingsStatus').className = 'settings-status configured';
                    document.getElementById('settingsStatus').textContent = 'Configured';
                    document.getElementById('jvmOptions').value = data.settings.jvm_options || '-Xmx2G -XX:+UseParallelGC';
                    document.getElementById('mavenProfiles').value = (data.settings.default_profiles || []).join(',');
                    document.getElementById('groupInfo').textContent = `Settings file: ${data.settings.settings_xml_path ? '✓ Uploaded' : '✗ Not uploaded'}`;
                } else {
                    document.getElementById('settingsStatus').className = 'settings-status not-configured';
                    document.getElementById('settingsStatus').textContent = 'Not Configured';
                    document.getElementById('groupInfo').textContent = 'Please upload settings.xml and configure options';
                }
            } catch (error) {
                console.error('Error checking group settings:', error);
            }
        }

        async function saveGroupSettings() {
            const groupId = document.getElementById('groupSelect').value;
            if (!groupId) {
                alert('Please select a group first');
                return;
            }

            if (!settingsFileContent) {
                alert('Please upload a settings.xml file');
                return;
            }

            const jvmOptions = document.getElementById('jvmOptions').value;
            const mavenProfiles = document.getElementById('mavenProfiles').value
                .split(',')
                .map(p => p.trim())
                .filter(p => p.length > 0);

            setButtonLoading('btnSaveSettings', true, 'Saving...');

            try {
                const response = await fetch('/api/group/settings', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        group_id: groupId,
                        settings_xml_content: settingsFileContent,
                        jvm_options: jvmOptions,
                        maven_profiles: mavenProfiles
                    })
                });

                const data = await response.json();
                alert(data.message);
                await checkGroupSettings();
            } catch (error) {
                alert('Error saving settings: ' + error);
            } finally {
                setButtonLoading('btnSaveSettings', false);
            }
        }

        async function loadProjects() {
            const groupId = document.getElementById('groupSelect').value;
            if (!groupId) {
                alert('Please select a group first');
                return;
            }

            const statusElement = document.getElementById('settingsStatus');
            if (statusElement.classList.contains('not-configured')) {
                if (!confirm('Group settings are not configured. Do you want to continue loading projects?')) {
                    return;
                }
            }

            setButtonLoading('btnLoadProjects', true, 'Loading...');
            updateStatus('Loading projects...');

            try {
                const response = await fetch(`/api/projects/${groupId}`);
                const data = await response.json();

                currentProjects = data.projects;
                const servicesList = document.getElementById('servicesList');
                servicesList.innerHTML = '';
                selectedServices.clear();

                if (data.projects.length === 0) {
                    servicesList.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;">No projects found in this group</div>';
                    updateStatus('No projects found');
                    return;
                }

                data.projects.forEach(project => {
                    const div = document.createElement('div');
                    div.className = 'service-item';
                    div.dataset.projectId = project.id;

                    const serviceName = document.createElement('span');
                    serviceName.className = 'service-name';
                    serviceName.textContent = project.name;

                    const branchSelect = document.createElement('select');
                    branchSelect.className = 'branch-selector';
                    branchSelect.onclick = (e) => e.stopPropagation();

                    // Add default branch
                    const defaultBranch = project.default_branch || 'master';
                    const defaultOption = document.createElement('option');
                    defaultOption.value = defaultBranch;
                    defaultOption.textContent = `${defaultBranch} (default)`;
                    branchSelect.appendChild(defaultOption);

                    // Load branches dynamically when selected
                    branchSelect.addEventListener('click', async function(e) {
                        e.stopPropagation();
                        if (this.dataset.loaded !== 'true') {
                            try {
                                const branchResponse = await fetch(`/api/project/${project.id}/branches`);
                                const branchData = await branchResponse.json();

                                // Clear and repopulate
                                this.innerHTML = '';
                                branchData.branches.forEach(branch => {
                                    const option = document.createElement('option');
                                    option.value = branch;
                                    option.textContent = branch === defaultBranch ? `${branch} (default)` : branch;
                                    this.appendChild(option);
                                });
                                this.value = defaultBranch;
                                this.dataset.loaded = 'true';
                            } catch (error) {
                                console.error('Error loading branches:', error);
                            }
                        }
                    });

                    div.appendChild(serviceName);
                    div.appendChild(branchSelect);

                    div.onclick = (e) => {
                        if (e.target === branchSelect) return;
                        toggleService(project, div, branchSelect);
                    };

                    servicesList.appendChild(div);
                });

                updateStatus(`Loaded ${data.projects.length} projects`);
            } catch (error) {
                alert('Error loading projects: ' + error);
            } finally {
                setButtonLoading('btnLoadProjects', false);
            }
        }

        function toggleService(project, element, branchSelect) {
            const serviceName = project.name;

            if (selectedServices.has(serviceName)) {
                selectedServices.delete(serviceName);
                element.classList.remove('selected');
            } else {
                const selectedBranch = branchSelect.value;
                selectedServices.set(serviceName, {
                    name: serviceName,
                    branch: selectedBranch,
                    repo_url: project.http_url_to_repo
                });
                element.classList.add('selected');
            }

            // Update branch when changed
            branchSelect.addEventListener('change', function(e) {
                e.stopPropagation();
                if (selectedServices.has(serviceName)) {
                    selectedServices.set(serviceName, {
                        name: serviceName,
                        branch: this.value,
                        repo_url: project.http_url_to_repo
                    });
                }
            });
        }

        async function buildSelected() {
            if (selectedServices.size === 0) {
                alert('Please select at least one service');
                return;
            }

            const groupId = document.getElementById('groupSelect').value;
            const force = document.getElementById('forceRebuild').checked;
            const maxWorkers = parseInt(document.getElementById('maxWorkers').value);

            document.getElementById('logOutput').innerHTML = '';
            updateStatus(`Building ${selectedServices.size} services...`);

            // Disable build buttons and show loading - FIXED
            disableBuildButtons();

            try {
                // Convert Map to array of build configs
                const buildConfigs = Array.from(selectedServices.values());

                const response = await fetch('/api/build', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        group_id: groupId,
                        build_configs: buildConfigs,  // Send with branch info
                        force: force,
                        max_workers: maxWorkers
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    updateStatus(data.message);
                } else {
                    alert('Error: ' + data.error);
                    updateStatus('Build failed to start');
                    enableBuildButtons();
                }
            } catch (error) {
                alert('Error starting build: ' + error);
                enableBuildButtons();
            }
        }

        async function buildAll() {
            const groupId = document.getElementById('groupSelect').value;
            if (!groupId) {
                alert('Please select a group first');
                return;
            }

            const servicesList = document.querySelectorAll('.service-item');
            if (servicesList.length === 0) {
                alert('No services loaded. Please load projects first.');
                return;
            }

            // Select all services with their respective branches
            selectedServices.clear();
            servicesList.forEach(item => {
                const projectId = item.dataset.projectId;
                const project = currentProjects.find(p => p.id == projectId);
                if (project) {
                    const branchSelect = item.querySelector('.branch-selector');
                    const selectedBranch = branchSelect ? branchSelect.value : (project.default_branch || 'master');

                    selectedServices.set(project.name, {
                        name: project.name,
                        branch: selectedBranch,
                        repo_url: project.http_url_to_repo
                    });
                    item.classList.add('selected');
                }
            });

            await buildSelected();
        }

        async function clearCache() {
            if (!confirm('Clear build cache? Next build will rebuild everything.')) return;

            setButtonLoading('btnClearCache', true, 'Clearing...');

            try {
                const response = await fetch('/api/cache/clear', {method: 'POST'});
                const data = await response.json();
                alert(data.message);
                updateStatus('Cache cleared');
            } catch (error) {
                alert('Error clearing cache: ' + error);
            } finally {
                setButtonLoading('btnClearCache', false);
            }
        }

        function clearLogs() {
            document.getElementById('logOutput').innerHTML = '';
            updateStatus('Logs cleared');
        }

        function updateStatus(message) {
            document.getElementById('statusBar').textContent = message;
        }

        // Load saved configuration on page load
        window.onload = function() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    if (data.gitlab_url) {
                        document.getElementById('gitlabUrl').value = data.gitlab_url;
                    }
                })
                .catch(error => console.error('Error loading config:', error));
        };
    </script>
</body>
</html>
"""