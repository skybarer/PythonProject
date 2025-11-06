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
            max-width: 1200px;
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
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover { background: #5a6268; }
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        .btn-danger:hover { background: #c82333; }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover { background: #218838; }
        .btn-info {
            background: #17a2b8;
            color: white;
        }
        .btn-info:hover { background: #138496; }
        #servicesList {
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 10px;
            max-height: 300px;
            overflow-y: auto;
            background: white;
        }
        .service-item {
            padding: 8px;
            margin-bottom: 5px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .service-item:hover { background: #e9ecef; }
        .service-item.selected {
            background: #667eea;
            color: white;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Microservice Build Automation</h1>
            <p>Parallel builds with intelligent caching for Spring Boot services</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>System Prerequisites</h2>
                <button class="btn btn-info" onclick="checkPrerequisites()">Check Git & Maven</button>
                <div id="prereqStatus" class="prereq-status" style="display: none;"></div>

                <div style="margin-top: 15px;">
                    <h3 style="font-size: 1.1em; margin-bottom: 10px;">Manual Configuration (if not detected)</h3>
                    <div class="form-group">
                        <label>Maven Path (optional - e.g., C:\path\to\apache-maven-3.9.9\bin\mvn.cmd)</label>
                        <input type="text" id="mavenPath" placeholder="Leave empty for auto-detection">
                    </div>
                    <button class="btn btn-success" onclick="setMavenPath()">Set Maven Path</button>
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
                <button class="btn btn-primary" onclick="connectGitLab()">Connect to GitLab</button>
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

                <button class="btn btn-success" onclick="saveGroupSettings()">Save Group Settings</button>
                <button class="btn btn-secondary" onclick="loadProjects()">Load Projects</button>
            </div>

            <div class="section">
                <h2>Build Services</h2>
                <div class="form-group">
                    <label>Services (Click to select multiple)</label>
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
                <button class="btn btn-primary" onclick="buildSelected()">Build Selected</button>
                <button class="btn btn-secondary" onclick="buildAll()">Build All</button>
                <button class="btn btn-danger" onclick="clearCache()">Clear Cache</button>
                <button class="btn btn-info" onclick="clearLogs()">Clear Logs</button>
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
        let selectedServices = new Set();
        let settingsFileContent = null;

        socket.on('log', function(data) {
            const logOutput = document.getElementById('logOutput');
            const message = data.message.replace(/\n/g, '<br>');
            logOutput.innerHTML += message + '<br>';
            logOutput.scrollTop = logOutput.scrollHeight;
        });

        socket.on('build_complete', function(data) {
            const status = `Build Complete - Success: ${data.success}, Failed: ${data.failed}, Skipped: ${data.skipped}`;
            updateStatus(status);

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
            }
        }

        async function setMavenPath() {
            const mavenPath = document.getElementById('mavenPath').value.trim();

            if (!mavenPath) {
                alert('Please enter a Maven path');
                return;
            }

            try {
                const response = await fetch('/api/set-maven-path', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({maven_path: mavenPath})
                });

                const data = await response.json();

                if (data.success) {
                    alert('Maven path set successfully! Click "Check Git & Maven" to verify.');
                    checkPrerequisites();
                } else {
                    alert('Failed to set Maven path: ' + data.error);
                }
            } catch (error) {
                alert('Error setting Maven path: ' + error);
            }
        }

        async function connectGitLab() {
            const url = document.getElementById('gitlabUrl').value;
            const token = document.getElementById('privateToken').value;

            if (!url || !token) {
                alert('Please enter GitLab URL and token');
                return;
            }

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
                checkGroupSettings();
            } catch (error) {
                alert('Error saving settings: ' + error);
            }
        }

        async function loadProjects() {
            const groupId = document.getElementById('groupSelect').value;
            if (!groupId) {
                alert('Please select a group first');
                return;
            }

            // Check if settings are configured
            const statusElement = document.getElementById('settingsStatus');
            if (statusElement.classList.contains('not-configured')) {
                if (!confirm('Group settings are not configured. Do you want to continue loading projects?')) {
                    return;
                }
            }

            updateStatus('Loading projects...');

            try {
                const response = await fetch(`/api/projects/${groupId}`);
                const data = await response.json();

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
                    div.textContent = project.name;
                    div.onclick = () => toggleService(project.name, div);
                    servicesList.appendChild(div);
                });

                updateStatus(`Loaded ${data.projects.length} projects`);
            } catch (error) {
                alert('Error loading projects: ' + error);
            }
        }

        function toggleService(serviceName, element) {
            if (selectedServices.has(serviceName)) {
                selectedServices.delete(serviceName);
                element.classList.remove('selected');
            } else {
                selectedServices.add(serviceName);
                element.classList.add('selected');
            }
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

            try {
                const response = await fetch('/api/build', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        group_id: groupId,
                        services: Array.from(selectedServices),
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
                }
            } catch (error) {
                alert('Error starting build: ' + error);
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

            selectedServices.clear();
            servicesList.forEach(item => {
                selectedServices.add(item.textContent);
                item.classList.add('selected');
            });

            await buildSelected();
        }

        async function clearCache() {
            if (!confirm('Clear build cache? Next build will rebuild everything.')) return;

            try {
                const response = await fetch('/api/cache/clear', {method: 'POST'});
                const data = await response.json();
                alert(data.message);
                updateStatus('Cache cleared');
            } catch (error) {
                alert('Error clearing cache: ' + error);
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
            // Check if there's a saved configuration
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