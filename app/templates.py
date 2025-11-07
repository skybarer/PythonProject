"""
UI templates with sequential loading:
1. Load microservices list first (fast)
2. Fetch branches on-demand when service is selected
3. Build with selected branches
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
        .form-group { margin-bottom: 15px; }
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
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover:not(:disabled) { background: #5a6268; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-danger:hover:not(:disabled) { background: #c82333; }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover:not(:disabled) { background: #218838; }
        .btn-info { background: #17a2b8; color: white; }
        .btn-info:hover:not(:disabled) { background: #138496; }
        
        .btn.loading {
            pointer-events: none;
            padding-right: 40px;
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
        
        #servicesTable {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 6px;
            overflow: hidden;
        }
        
        #servicesTable thead {
            background: #667eea;
            color: white;
        }
        
        #servicesTable th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        #servicesTable td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        
        #servicesTable tr:hover {
            background: #f8f9fa;
        }
        
        .service-checkbox {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .branch-select {
            width: 100%;
            padding: 6px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .branch-select:disabled {
            background: #f0f0f0;
            cursor: not-allowed;
        }
        
        .service-name {
            font-weight: 500;
            color: #333;
        }
        
        .default-branch-badge {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 8px;
        }
        
        .select-all-container {
            background: #e7f3ff;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        
        .select-all-container label {
            margin: 0 0 0 8px;
            font-weight: 500;
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
        .prereq-item:last-child { border-bottom: none; }
        .prereq-ok { color: #28a745; font-weight: 600; }
        .prereq-error { color: #dc3545; font-weight: 600; }
        .loading-spinner {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .info-badge {
            display: inline-block;
            background: #17a2b8;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Microservice Build Automation</h1>
            <p>Sequential loading: Microservices → Branches → Build</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>System Prerequisites</h2>
                <button class="btn btn-info" id="btnCheckPrereq" onclick="checkPrerequisites()">Check Git, Java & Maven</button>
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
                <button class="btn btn-secondary" id="btnLoadProjects" onclick="loadProjects()">Load Microservices</button>
            </div>

            <div class="section">
                <h2>Build Services <span id="projectCount" class="info-badge" style="display: none;">0 services</span></h2>
                
                <div class="select-all-container">
                    <input type="checkbox" id="selectAllCheckbox" onchange="toggleSelectAll()">
                    <label for="selectAllCheckbox">Select All Services</label>
                    <button class="btn btn-info" onclick="fetchAllBranches()" id="btnFetchAllBranches" style="margin-left: auto; display: none;">
                        Fetch All Branches
                    </button>
                </div>
                
                <div style="overflow-x: auto;">
                    <table id="servicesTable">
                        <thead>
                            <tr>
                                <th style="width: 50px;">Select</th>
                                <th>Service Name</th>
                                <th style="width: 250px;">Branch</th>
                                <th style="width: 100px;">Status</th>
                            </tr>
                        </thead>
                        <tbody id="servicesTableBody">
                            <tr>
                                <td colspan="4" style="text-align: center; padding: 40px; color: #999;">
                                    No projects loaded. Please select a group and click "Load Microservices".
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div style="margin-top: 20px;">
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
        let settingsFileContent = null;
        let projectsData = [];

        socket.on('log', function(data) {
            const logOutput = document.getElementById('logOutput');
            const message = data.message.replace(/\n/g, '<br>');
            logOutput.innerHTML += message + '<br>';
            logOutput.scrollTop = logOutput.scrollHeight;
        });

        socket.on('build_complete', function(data) {
            const status = `Build Complete - Success: ${data.success}, Failed: ${data.failed}, Skipped: ${data.skipped}`;
            updateStatus(status);
            enableBuildButtons();

            const logOutput = document.getElementById('logOutput');
            logOutput.innerHTML += '<br><span style="color: #4CAF50; font-weight: bold;">========================================</span><br>';
            logOutput.innerHTML += '<span style="color: #4CAF50; font-weight: bold;">BUILD SUMMARY</span><br>';
            logOutput.innerHTML += '<span style="color: #4CAF50; font-weight: bold;">========================================</span><br>';
            logOutput.innerHTML += `<span style="color: #4CAF50;">✅ Success: ${data.success}</span><br>`;
            logOutput.innerHTML += `<span style="color: #f44336;">❌ Failed: ${data.failed}</span><br>`;
            logOutput.innerHTML += `<span style="color: #FF9800;">⭐️ Skipped: ${data.skipped}</span><br>`;
            logOutput.innerHTML += '<span style="color: #4CAF50; font-weight: bold;">========================================</span><br>';
            logOutput.scrollTop = logOutput.scrollHeight;
        });

        function setButtonLoading(buttonId, loading) {
            const btn = document.getElementById(buttonId);
            if (!btn) return;
            
            if (loading) {
                btn.disabled = true;
                btn.classList.add('loading');
                btn.dataset.originalText = btn.textContent;
                btn.textContent = 'Loading...';
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
            ['btnBuildSelected', 'btnBuildAll'].forEach(id => {
                const btn = document.getElementById(id);
                if (btn) {
                    btn.disabled = true;
                    btn.classList.add('loading');
                }
            });
        }

        function enableBuildButtons() {
            ['btnBuildSelected', 'btnBuildAll'].forEach(id => {
                const btn = document.getElementById(id);
                if (btn) {
                    btn.disabled = false;
                    btn.classList.remove('loading');
                    if (btn.dataset.originalText) {
                        btn.textContent = btn.dataset.originalText;
                        delete btn.dataset.originalText;
                    }
                }
            });
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

                const gitClass = data.git.available ? 'prereq-ok' : 'prereq-error';
                html += `<div class="prereq-item">
                    <span><strong>Git:</strong> ${data.git.version}</span>
                    <span class="${gitClass}">${data.git.available ? '✓ Available' : '✗ Not Found'}</span>
                </div>`;
                if (data.git.path) {
                    html += `<div style="font-size: 12px; color: #666; padding: 5px 0;">Path: ${data.git.path}</div>`;
                }

                const mavenClass = data.maven.available ? 'prereq-ok' : 'prereq-error';
                html += `<div class="prereq-item">
                    <span><strong>Maven:</strong> ${data.maven.version}</span>
                    <span class="${mavenClass}">${data.maven.available ? '✓ Available' : '✗ Not Found'}</span>
                </div>`;
                if (data.maven.path) {
                    html += `<div style="font-size: 12px; color: #666; padding: 5px 0;">Path: ${data.maven.path}</div>`;
                } else {
                    html += `<div style="font-size: 12px; color: #dc3545; padding: 5px 0;">
                        ⚠️ Maven not found. Please set the path manually below.
                    </div>`;
                }

                prereqStatus.innerHTML = html;
                prereqStatus.style.display = 'block';

                if (!data.git.available || !data.maven.available) {
                    updateStatus('⚠️ Prerequisites not met');
                } else {
                    updateStatus('✓ All prerequisites satisfied');
                }
            } catch (error) {
                alert('Error checking prerequisites: ' + error);
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
                    alert('Maven path set successfully!');
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

            setButtonLoading('btnConnect', true);
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
                    document.getElementById('groupInfo').textContent = 'Please upload settings.xml';
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

            setButtonLoading('btnSaveSettings', true);

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

        // STEP 1: Load microservices list (fast)
        async function loadProjects() {
            const groupId = document.getElementById('groupSelect').value;
            if (!groupId) {
                alert('Please select a group first');
                return;
            }

            setButtonLoading('btnLoadProjects', true);
            updateStatus('Loading microservices...');

            const tbody = document.getElementById('servicesTableBody');
            tbody.innerHTML = '<tr><td colspan="4" class="loading-spinner">Loading microservices...</td></tr>';

            try {
                const response = await fetch(`/api/projects/${groupId}`);
                const data = await response.json();
                projectsData = data.projects.map(project => ({
                    ...project,
                    branches: [project.default_branch],
                    selectedBranch: project.default_branch,
                    branchesLoaded: false,
                    branchesLoading: false
                }));

                if (projectsData.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 40px; color: #999;">No projects found in this group</td></tr>';
                    updateStatus('No projects found');
                    document.getElementById('projectCount').style.display = 'none';
                    document.getElementById('btnFetchAllBranches').style.display = 'none';
                    return;
                }

                renderProjectsTable();
                updateStatus(`Loaded ${projectsData.length} microservices`);
                document.getElementById('projectCount').textContent = `${projectsData.length} services`;
                document.getElementById('projectCount').style.display = 'inline-block';
                document.getElementById('btnFetchAllBranches').style.display = 'inline-block';
            } catch (error) {
                alert('Error loading projects: ' + error);
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 40px; color: #dc3545;">Error loading projects</td></tr>';
            } finally {
                setButtonLoading('btnLoadProjects', false);
            }
        }

        // STEP 2: Fetch branches for a specific project (on-demand)
        async function loadBranchesForProject(index) {
            const project = projectsData[index];
            
            // Skip if already loaded or loading
            if (project.branchesLoaded || project.branchesLoading) {
                return;
            }

            project.branchesLoading = true;
            updateProjectStatus(index, 'Loading branches...');

            try {
                const response = await fetch(`/api/project/${project.id}/branches`);
                const data = await response.json();
                
                if (data.branches && data.branches.length > 0) {
                    project.branches = data.branches;
                    project.branchesLoaded = true;
                    updateProjectStatus(index, `${data.branches.length} branches`);
                    
                    // Update the branch select dropdown
                    const branchSelect = document.querySelector(`.branch-select[data-index="${index}"]`);
                    if (branchSelect) {
                        let branchOptions = '';
                        project.branches.forEach(branch => {
                            const isDefault = branch === project.default_branch;
                            const selected = branch === project.selectedBranch ? 'selected' : '';
                            branchOptions += `<option value="${branch}" ${selected}>${branch}${isDefault ? ' (default)' : ''}</option>`;
                        });
                        branchSelect.innerHTML = branchOptions;
                    }
                } else {
                    updateProjectStatus(index, 'No branches found');
                }
            } catch (error) {
                console.error(`Error loading branches for ${project.name}:`, error);
                updateProjectStatus(index, 'Error loading branches');
            } finally {
                project.branchesLoading = false;
            }
        }

        // Fetch all branches for all projects
        async function fetchAllBranches() {
            if (projectsData.length === 0) {
                alert('No projects loaded');
                return;
            }

            setButtonLoading('btnFetchAllBranches', true);
            updateStatus('Fetching branches for all projects...');

            const promises = [];
            for (let i = 0; i < projectsData.length; i++) {
                if (!projectsData[i].branchesLoaded) {
                    promises.push(loadBranchesForProject(i));
                }
            }

            await Promise.all(promises);
            updateStatus(`Fetched branches for ${projectsData.length} projects`);
            setButtonLoading('btnFetchAllBranches', false);
        }

        function updateProjectStatus(index, status) {
            const statusCell = document.querySelector(`.status-cell[data-index="${index}"]`);
            if (statusCell) {
                statusCell.textContent = status;
            }
        }

        function renderProjectsTable() {
            const tbody = document.getElementById('servicesTableBody');
            tbody.innerHTML = '';

            projectsData.forEach((project, index) => {
                const row = document.createElement('tr');
                
                // Checkbox cell
                const checkboxCell = document.createElement('td');
                checkboxCell.innerHTML = `<input type="checkbox" class="service-checkbox" data-index="${index}" onchange="handleServiceCheckboxChange(${index})">`;
                row.appendChild(checkboxCell);

                // Service name cell
                const nameCell = document.createElement('td');
                nameCell.innerHTML = `<span class="service-name">${project.name}</span>`;
                row.appendChild(nameCell);

                // Branch selection cell
                const branchCell = document.createElement('td');
                let branchOptions = '';
                project.branches.forEach(branch => {
                    const isDefault = branch === project.default_branch;
                    const selected = branch === project.selectedBranch ? 'selected' : '';
                    branchOptions += `<option value="${branch}" ${selected}>${branch}${isDefault ? ' (default)' : ''}</option>`;
                });
                
                branchCell.innerHTML = `
                    <select class="branch-select" data-index="${index}" onchange="handleBranchChange(${index}, this.value)">
                        ${branchOptions}
                    </select>
                `;
                row.appendChild(branchCell);

                // Status cell
                const statusCell = document.createElement('td');
                statusCell.className = 'status-cell';
                statusCell.setAttribute('data-index', index);
                statusCell.textContent = 'Default branch';
                statusCell.style.fontSize = '12px';
                statusCell.style.color = '#666';
                row.appendChild(statusCell);

                tbody.appendChild(row);
            });
        }

        async function handleServiceCheckboxChange(index) {
            const checkbox = document.querySelector(`.service-checkbox[data-index="${index}"]`);
            const project = projectsData[index];
            
            // Load branches when service is selected for the first time
            if (checkbox.checked && !project.branchesLoaded && !project.branchesLoading) {
                await loadBranchesForProject(index);
            }
        }

        function handleBranchChange(index, value) {
            projectsData[index].selectedBranch = value;
        }

        function toggleSelectAll() {
            const selectAll = document.getElementById('selectAllCheckbox').checked;
            const checkboxes = document.querySelectorAll('.service-checkbox');
            checkboxes.forEach((cb, index) => {
                cb.checked = selectAll;
                if (selectAll) {
                    handleServiceCheckboxChange(index);
                }
            });
        }

        function getSelectedServices() {
            const selected = [];
            const checkboxes = document.querySelectorAll('.service-checkbox:checked');
            
            checkboxes.forEach(checkbox => {
                const index = parseInt(checkbox.dataset.index);
                const project = projectsData[index];
                selected.push({
                    name: project.name,
                    repo_url: project.http_url_to_repo,
                    branch: project.selectedBranch
                });
            });

            return selected;
        }

        // STEP 3: Build with selected branches
        async function buildSelected() {
            const selectedServices = getSelectedServices();
            
            if (selectedServices.length === 0) {
                alert('Please select at least one service');
                return;
            }

            const groupId = document.getElementById('groupSelect').value;
            const force = document.getElementById('forceRebuild').checked;
            const maxWorkers = parseInt(document.getElementById('maxWorkers').value);

            document.getElementById('logOutput').innerHTML = '';
            updateStatus(`Building ${selectedServices.length} services...`);

            disableBuildButtons();

            try {
                const response = await fetch('/api/build', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        group_id: groupId,
                        build_configs: selectedServices,
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

            if (projectsData.length === 0) {
                alert('No services loaded. Please load projects first.');
                return;
            }

            // Select all checkboxes
            document.getElementById('selectAllCheckbox').checked = true;
            toggleSelectAll();

            await buildSelected();
        }

        async function clearCache() {
            if (!confirm('Clear build cache? Next build will rebuild everything.')) return;

            setButtonLoading('btnClearCache', true);

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