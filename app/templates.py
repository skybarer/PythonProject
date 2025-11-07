"""
UI templates with enterprise-scale improvements:
1. Group filter for large number of groups
2. Service search/filter for hundreds of microservices
3. Config file dropdown with refresh
4. Save/clear credentials
5. Profile management
6. Better branch display with default badge
7. Responsive table with scroll
8. Modern UI with better visual hierarchy
"""

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Microservice Build Automation</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 12px;
            font-weight: 700;
        }
        
        .header p { 
            opacity: 0.95;
            font-size: 1.1em;
        }
        
        .content { 
            padding: 30px;
            max-height: calc(100vh - 250px);
            overflow-y: auto;
        }
        
        .section {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #e9ecef;
        }
        
        .section h2 {
            font-size: 1.4em;
            margin-bottom: 20px;
            color: #333;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .form-group { 
            margin-bottom: 16px; 
        }
        
        label {
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            color: #495057;
            font-size: 14px;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 10px 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.2s;
            font-family: inherit;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .search-input {
            position: relative;
        }
        
        .search-input input {
            padding-left: 40px;
        }
        
        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #6c757d;
            font-size: 18px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-right: 10px;
            margin-bottom: 10px;
            position: relative;
            display: inline-flex;
            align-items: center;
            gap: 8px;
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
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); 
        }
        
        .btn-secondary { 
            background: #6c757d; 
            color: white; 
        }
        
        .btn-secondary:hover:not(:disabled) { 
            background: #5a6268; 
        }
        
        .btn-danger { 
            background: #dc3545; 
            color: white; 
        }
        
        .btn-danger:hover:not(:disabled) { 
            background: #c82333; 
        }
        
        .btn-success { 
            background: #28a745; 
            color: white; 
        }
        
        .btn-success:hover:not(:disabled) { 
            background: #218838; 
        }
        
        .btn-info { 
            background: #17a2b8; 
            color: white; 
        }
        
        .btn-info:hover:not(:disabled) { 
            background: #138496; 
        }
        
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
        
        .table-container {
            max-height: 600px;
            overflow: auto;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background: white;
        }
        
        #servicesTable {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        
        #servicesTable thead {
            background: #667eea;
            color: white;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        #servicesTable th {
            padding: 14px 12px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        #servicesTable td {
            padding: 12px;
            border-bottom: 1px solid #f1f3f5;
            font-size: 14px;
        }
        
        #servicesTable tbody tr:hover {
            background: #f8f9fa;
        }
        
        .service-checkbox {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        .branch-container {
            position: relative;
            width: 100%;
            min-width: 250px;
        }
        
        .branch-search-wrapper {
            position: relative;
            margin-bottom: 6px;
        }
        
        .branch-search {
            width: 100%;
            padding: 6px 10px;
            padding-right: 30px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            font-size: 13px;
        }
        
        .branch-search:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .branch-select {
            width: 100%;
            padding: 6px 10px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            font-size: 13px;
            max-height: 150px;
            background: white;
        }
        
        .branch-select:disabled {
            background: #f0f0f0;
            cursor: not-allowed;
        }
        
        .branch-select option {
            padding: 6px;
        }
        
        .service-name {
            font-weight: 500;
            color: #212529;
        }
        
        .default-branch-badge {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 8px;
            font-weight: 600;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-danger {
            background: #f8d7da;
            color: #721c24;
        }
        
        .badge-info {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .badge-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .select-all-container {
            background: #e7f3ff;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .select-all-container label {
            margin: 0 0 0 8px;
            font-weight: 500;
        }
        
        #logOutput {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            height: 500px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .status-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 16px;
            text-align: center;
            font-weight: 600;
            color: white;
            font-size: 14px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin-right: 8px;
        }
        
        .file-upload-area {
            border: 2px dashed #dee2e6;
            border-radius: 8px;
            padding: 30px;
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
            border-style: solid;
        }
        
        .file-info {
            margin-top: 12px;
            padding: 12px;
            background: #e7f3ff;
            border-radius: 6px;
            font-size: 13px;
        }
        
        .prereq-status {
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            border: 1px solid #e9ecef;
        }
        
        .prereq-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f1f3f5;
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
        
        .loading-spinner {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .info-badge {
            display: inline-block;
            background: #17a2b8;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 8px;
            font-weight: 600;
        }
        
        .branch-loading {
            font-size: 13px;
            color: #17a2b8;
            font-style: italic;
        }
        
        .branch-count {
            font-size: 11px;
            color: #6c757d;
            margin-top: 4px;
        }
        
        .no-branches {
            font-size: 13px;
            color: #6c757d;
            font-style: italic;
        }
        
        .card {
            background: white;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #e9ecef;
            margin-bottom: 16px;
        }
        
        .card-title {
            font-weight: 600;
            margin-bottom: 12px;
            color: #333;
        }
        
        .refresh-btn {
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background 0.2s;
        }
        
        .refresh-btn:hover {
            background: #f8f9fa;
        }
        
        .credentials-saved {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .profile-chip {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            margin: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .profile-chip:hover {
            background: #5568d3;
        }
        
        .profile-chip .remove {
            margin-left: 6px;
            font-weight: bold;
            cursor: pointer;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f3f5;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #adb5bd;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #868e96;
        }
        
        .icon {
            font-size: 18px;
        }
        
        .collapsible-section {
            margin-bottom: 20px;
        }
        
        .collapsible-header {
            background: #667eea;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }
        
        .collapsible-header:hover {
            background: #5568d3;
        }
        
        .collapsible-content {
            padding: 20px;
            border: 1px solid #e9ecef;
            border-top: none;
            border-radius: 0 0 8px 8px;
            background: white;
        }
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Microservice Build Automation</h1>
            <p>Enterprise-scale microservice build management</p>
        </div>

        <div class="content">
            <!-- System Prerequisites Section -->
            <div class="collapsible-section">
                <div class="collapsible-header" onclick="toggleSection('prereqSection')">
                    <span><span class="icon">⚙️</span> System Prerequisites</span>
                    <span id="prereqToggle">▼</span>
                </div>
                <div id="prereqSection" class="collapsible-content">
                    <button class="btn btn-info" id="btnCheckPrereq" onclick="checkPrerequisites()">
                        <span class="icon">🔍</span> Check Git & Maven
                    </button>
                    <div id="prereqStatus" class="prereq-status" style="display: none;"></div>

                    <div style="margin-top: 20px;">
                        <h3 style="font-size: 1.1em; margin-bottom: 12px; font-weight: 600;">Manual Configuration</h3>
                        <div class="form-group">
                            <label>Maven Path (optional)</label>
                            <input type="text" id="mavenPath" placeholder="C:\path\to\apache-maven-3.9.9\bin\mvn.cmd">
                        </div>
                        <button class="btn btn-success" id="btnSetMaven" onclick="setMavenPath()">
                            <span class="icon">✔️</span> Set Maven Path
                        </button>
                    </div>
                </div>
            </div>

            <!-- GitLab Configuration Section -->
            <div class="section">
                <h2><span class="icon">🔗</span> GitLab Configuration</h2>
                
                <div id="savedCredentials" style="display: none;" class="credentials-saved">
                    <span>✅ Credentials saved and connected</span>
                    <button class="btn btn-danger" onclick="clearCredentials()">Clear Credentials</button>
                </div>
                
                <div id="credentialsForm">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>GitLab URL</label>
                            <input type="text" id="gitlabUrl" placeholder="https://gitlab.com" value="https://gitlab.com">
                        </div>
                        <div class="form-group">
                            <label>Private Token</label>
                            <input type="password" id="privateToken" placeholder="Enter your GitLab private token">
                        </div>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="saveCredentials">
                        <label for="saveCredentials" style="margin: 0;">Save credentials locally (encrypted in browser)</label>
                    </div>
                    <button class="btn btn-primary" id="btnConnect" onclick="connectGitLab()">
                        <span class="icon">🔌</span> Connect to GitLab
                    </button>
                </div>
            </div>

            <!-- Group Configuration Section -->
            <div class="section">
                <h2><span class="icon">📁</span> Group & Build Configuration</h2>
                
                <div class="form-group">
                    <label>Search Groups <span id="groupCount" class="badge badge-info" style="display: none;">0 groups</span></label>
                    <div class="search-input">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="groupSearch" placeholder="Filter groups..." oninput="filterGroups()">
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Group <span id="settingsStatus" class="badge badge-danger">Not Configured</span></label>
                    <select id="groupSelect" size="8" onchange="checkGroupSettings()" style="min-height: 150px;">
                        <option value="">-- Select a group --</option>
                    </select>
                </div>

                <div class="card">
                    <div class="card-title">Maven Configuration</div>
                    
                    <div class="form-group">
                        <label>
                            Settings File (settings.xml)
                            <span class="refresh-btn" onclick="refreshSettingsFiles()" title="Refresh list">🔄</span>
                        </label>
                        <select id="settingsFileDropdown" onchange="handleSettingsFileSelection()">
                            <option value="">-- Select existing or upload new --</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Or Upload New Settings File</label>
                        <div class="file-upload-area" id="fileUploadArea" onclick="document.getElementById('settingsFile').click()">
                            <div>📄 Click or drag to upload settings.xml</div>
                            <input type="file" id="settingsFile" accept=".xml" style="display: none;" onchange="handleFileSelect(event)">
                        </div>
                        <div id="fileInfo" class="file-info" style="display: none;"></div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label>JVM Options</label>
                            <input type="text" id="jvmOptions" placeholder="-Xmx2G -XX:+UseParallelGC" value="-Xmx2G -XX:+UseParallelGC">
                        </div>
                        
                        <div class="form-group">
                            <label>Maven Threads</label>
                            <input type="number" id="mavenThreads" value="4" min="1" max="16">
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Maven Profiles</label>
                        <input type="text" id="mavenProfilesInput" placeholder="Type profile and press Enter">
                        <div id="profilesContainer" style="margin-top: 8px;"></div>
                    </div>

                    <button class="btn btn-success" id="btnSaveSettings" onclick="saveGroupSettings()">
                        <span class="icon">💾</span> Save Group Settings
                    </button>
                    <button class="btn btn-secondary" id="btnLoadProjects" onclick="loadProjects()">
                        <span class="icon">📦</span> Load Microservices
                    </button>
                </div>
            </div>

            <!-- Build Services Section -->
            <div class="section">
                <h2>
                    <span class="icon">🔨</span> Build Services 
                    <span id="projectCount" class="info-badge" style="display: none;">0 services</span>
                </h2>
                
                <div class="form-group">
                    <label>Search Services</label>
                    <div class="search-input">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="serviceSearch" placeholder="Filter services..." oninput="filterServices()">
                    </div>
                </div>
                
                <div class="select-all-container">
                    <div>
                        <input type="checkbox" id="selectAllCheckbox" onchange="toggleSelectAll()">
                        <label for="selectAllCheckbox">Select All Services</label>
                    </div>
                    <div>
                        <span id="selectionInfo" style="font-size: 13px; color: #333; font-weight: 600;"></span>
                    </div>
                </div>
                
                <div class="table-container">
                    <table id="servicesTable">
                        <thead>
                            <tr>
                                <th style="width: 50px;">Select</th>
                                <th style="min-width: 200px;">Service Name</th>
                                <th style="width: 300px;">Branch Selection</th>
                            </tr>
                        </thead>
                        <tbody id="servicesTableBody">
                            <tr>
                                <td colspan="3" style="text-align: center; padding: 60px; color: #6c757d;">
                                    <div style="font-size: 48px; margin-bottom: 16px;">📦</div>
                                    <div style="font-size: 16px;">No projects loaded</div>
                                    <div style="font-size: 14px; margin-top: 8px;">Select a group and click "Load Microservices"</div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div style="margin-top: 20px;">
                    <div class="form-grid">
                        <div class="checkbox-group">
                            <input type="checkbox" id="forceRebuild">
                            <label for="forceRebuild" style="margin-bottom: 0;">Force rebuild (ignore cache)</label>
                        </div>
                        <div class="form-group">
                            <label>Parallel Builds</label>
                            <input type="number" id="maxWorkers" value="4" min="1" max="16">
                        </div>
                    </div>
                    
                    <button class="btn btn-primary" id="btnBuildSelected" onclick="buildSelected()">
                        <span class="icon">🚀</span> Build Selected
                    </button>
                    <button class="btn btn-secondary" id="btnBuildAll" onclick="buildAll()">
                        <span class="icon">🔨</span> Build All
                    </button>
                    <button class="btn btn-danger" id="btnClearCache" onclick="clearCache()">
                        <span class="icon">🗑️</span> Clear Cache
                    </button>
                    <button class="btn btn-info" id="btnClearLogs" onclick="clearLogs()">
                        <span class="icon">📋</span> Clear Logs
                    </button>
                </div>
            </div>

            <!-- Build Log Section -->
            <div class="section">
                <h2><span class="icon">📜</span> Build Log</h2>
                <div id="logOutput"></div>
            </div>
        </div>

        <div class="status-bar" id="statusBar">Ready to connect</div>
    </div>

    <script>
        const socket = io();
        let settingsFileContent = null;
        let projectsData = [];
        let branchCache = {};
        let allGroups = [];
        let mavenProfiles = [];

        // LocalStorage keys
        const STORAGE_KEYS = {
            GITLAB_URL: 'gitlab_url',
            GITLAB_TOKEN: 'gitlab_token_encrypted',
            CREDENTIALS_SAVED: 'credentials_saved'
        };

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
            logOutput.innerHTML += `<span style="color: #FF9800;">⭐ Skipped: ${data.skipped}</span><br>`;
            logOutput.innerHTML += '<span style="color: #4CAF50; font-weight: bold;">========================================</span><br>';
            logOutput.scrollTop = logOutput.scrollHeight;
        });

        // Collapsible sections
        function toggleSection(sectionId) {
            const section = document.getElementById(sectionId);
            const toggle = document.getElementById(sectionId.replace('Section', 'Toggle'));
            
            if (section.classList.contains('hidden')) {
                section.classList.remove('hidden');
                toggle.textContent = '▼';
            } else {
                section.classList.add('hidden');
                toggle.textContent = '▶';
            }
        }

        // Maven Profiles Management
        document.getElementById('mavenProfilesInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const value = this.value.trim();
                if (value && !mavenProfiles.includes(value)) {
                    mavenProfiles.push(value);
                    renderProfiles();
                    this.value = '';
                }
            }
        });

        function renderProfiles() {
            const container = document.getElementById('profilesContainer');
            container.innerHTML = '';
            mavenProfiles.forEach((profile, index) => {
                const chip = document.createElement('span');
                chip.className = 'profile-chip';
                chip.innerHTML = `${profile} <span class="remove" onclick="removeProfile(${index})">×</span>`;
                container.appendChild(chip);
            });
        }

        function removeProfile(index) {
            mavenProfiles.splice(index, 1);
            renderProfiles();
        }

        // Credentials Management
        function saveCredentialsToStorage(url, token) {
            localStorage.setItem(STORAGE_KEYS.GITLAB_URL, url);
            // Simple encoding (in production, use proper encryption)
            localStorage.setItem(STORAGE_KEYS.GITLAB_TOKEN, btoa(token));
            localStorage.setItem(STORAGE_KEYS.CREDENTIALS_SAVED, 'true');
        }

        function loadCredentialsFromStorage() {
            if (localStorage.getItem(STORAGE_KEYS.CREDENTIALS_SAVED) === 'true') {
                const url = localStorage.getItem(STORAGE_KEYS.GITLAB_URL);
                const encodedToken = localStorage.getItem(STORAGE_KEYS.GITLAB_TOKEN);
                
                if (url && encodedToken) {
                    return {
                        url: url,
                        token: atob(encodedToken)
                    };
                }
            }
            return null;
        }

        function clearCredentials() {
            if (!confirm('Clear saved credentials? You will need to re-enter them.')) return;
            
            localStorage.removeItem(STORAGE_KEYS.GITLAB_URL);
            localStorage.removeItem(STORAGE_KEYS.GITLAB_TOKEN);
            localStorage.removeItem(STORAGE_KEYS.CREDENTIALS_SAVED);
            
            document.getElementById('savedCredentials').style.display = 'none';
            document.getElementById('credentialsForm').style.display = 'block';
            document.getElementById('gitlabUrl').value = 'https://gitlab.com';
            document.getElementById('privateToken').value = '';
            document.getElementById('saveCredentials').checked = false;
            
            updateStatus('Credentials cleared');
        }

        function showSavedCredentials() {
            document.getElementById('savedCredentials').style.display = 'flex';
            document.getElementById('credentialsForm').style.display = 'none';
        }

        // Group filtering
        function filterGroups() {
            const searchTerm = document.getElementById('groupSearch').value.toLowerCase();
            const select = document.getElementById('groupSelect');
            const options = select.querySelectorAll('option');
            
            let visibleCount = 0;
            options.forEach(option => {
                if (option.value === '') {
                    option.style.display = '';
                    return;
                }
                
                const text = option.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    option.style.display = '';
                    visibleCount++;
                } else {
                    option.style.display = 'none';
                }
            });
            
            const badge = document.getElementById('groupCount');
            if (badge) {
                if (searchTerm) {
                    badge.textContent = `${visibleCount} of ${allGroups.length} groups`;
                } else {
                    badge.textContent = `${allGroups.length} groups`;
                }
            }
        }

        // Service filtering
        function filterServices() {
            const searchTerm = document.getElementById('serviceSearch').value.toLowerCase();
            const tbody = document.getElementById('servicesTableBody');
            const rows = tbody.querySelectorAll('tr');
            
            let visibleCount = 0;
            rows.forEach(row => {
                const nameCell = row.querySelector('.service-name');
                if (!nameCell) {
                    row.style.display = '';
                    return;
                }
                
                const serviceName = nameCell.textContent.toLowerCase();
                if (serviceName.includes(searchTerm)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });
            
            const badge = document.getElementById('projectCount');
            if (badge && projectsData.length > 0) {
                if (searchTerm) {
                    badge.textContent = `${visibleCount} of ${projectsData.length} services`;
                } else {
                    badge.textContent = `${projectsData.length} services`;
                }
            }
        }

        // Settings files management
        async function refreshSettingsFiles() {
            try {
                const response = await fetch('/api/settings-files');
                const data = await response.json();
                
                const dropdown = document.getElementById('settingsFileDropdown');
                dropdown.innerHTML = '<option value="">-- Select existing or upload new --</option>';
                
                data.files.forEach(file => {
                    const option = document.createElement('option');
                    option.value = file.name;
                    option.textContent = `${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
                    dropdown.appendChild(option);
                });
                
                updateStatus(`Loaded ${data.files.length} settings files`);
            } catch (error) {
                console.error('Error refreshing settings files:', error);
            }
        }

        function handleSettingsFileSelection() {
            const dropdown = document.getElementById('settingsFileDropdown');
            const selectedFile = dropdown.value;
            
            if (selectedFile) {
                settingsFileContent = null; // Clear uploaded content
                document.getElementById('fileInfo').style.display = 'block';
                document.getElementById('fileInfo').innerHTML = `✓ Selected: ${selectedFile}`;
            } else {
                document.getElementById('fileInfo').style.display = 'none';
            }
        }

        function setButtonLoading(buttonId, loading) {
            const btn = document.getElementById(buttonId);
            if (!btn) return;
            
            if (loading) {
                btn.disabled = true;
                btn.classList.add('loading');
                btn.dataset.originalText = btn.textContent;
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
                document.getElementById('settingsFileDropdown').value = ''; // Clear dropdown selection
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

                let html = '<h3 style="margin-bottom: 12px; font-weight: 600;">System Check Results:</h3>';

                const gitClass = data.git.available ? 'prereq-ok' : 'prereq-error';
                html += `<div class="prereq-item">
                    <span><strong>Git:</strong> ${data.git.version}</span>
                    <span class="${gitClass}">${data.git.available ? '✓ Available' : '✗ Not Found'}</span>
                </div>`;
                if (data.git.path) {
                    html += `<div style="font-size: 12px; color: #6c757d; padding: 5px 0;">Path: ${data.git.path}</div>`;
                }

                const mavenClass = data.maven.available ? 'prereq-ok' : 'prereq-error';
                html += `<div class="prereq-item">
                    <span><strong>Maven:</strong> ${data.maven.version}</span>
                    <span class="${mavenClass}">${data.maven.available ? '✓ Available' : '✗ Not Found'}</span>
                </div>`;
                if (data.maven.path) {
                    html += `<div style="font-size: 12px; color: #6c757d; padding: 5px 0;">Path: ${data.maven.path}</div>`;
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
            const saveCredentials = document.getElementById('saveCredentials').checked;

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
                    allGroups = data.groups;
                    const groupSelect = document.getElementById('groupSelect');
                    groupSelect.innerHTML = '<option value="">-- Select a group --</option>';
                    
                    data.groups.forEach(group => {
                        const option = document.createElement('option');
                        option.value = group.id;
                        option.textContent = `${group.full_path} (${group.name})`;
                        option.dataset.fullPath = group.full_path.toLowerCase();
                        groupSelect.appendChild(option);
                    });
                    
                    document.getElementById('groupCount').textContent = `${data.groups.length} groups`;
                    document.getElementById('groupCount').style.display = 'inline-block';
                    
                    updateStatus(`Connected! Loaded ${data.groups.length} groups`);
                    
                    // Save credentials if requested
                    if (saveCredentials) {
                        saveCredentialsToStorage(url, token);
                        showSavedCredentials();
                    }
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
                document.getElementById('settingsStatus').className = 'badge badge-danger';
                document.getElementById('settingsStatus').textContent = 'Not Configured';
                return;
            }

            try {
                const response = await fetch(`/api/group/settings/${groupId}`);
                const data = await response.json();

                if (data.configured) {
                    document.getElementById('settingsStatus').className = 'badge badge-success';
                    document.getElementById('settingsStatus').textContent = 'Configured';
                    document.getElementById('jvmOptions').value = data.settings.jvm_options || '-Xmx2G -XX:+UseParallelGC';
                    document.getElementById('mavenThreads').value = data.settings.maven_threads || 4;
                    mavenProfiles = data.settings.default_profiles || [];
                    renderProfiles();
                } else {
                    document.getElementById('settingsStatus').className = 'badge badge-warning';
                    document.getElementById('settingsStatus').textContent = 'Not Configured';
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

            const settingsFileName = document.getElementById('settingsFileDropdown').value;
            
            if (!settingsFileContent && !settingsFileName) {
                alert('Please select or upload a settings.xml file');
                return;
            }

            const jvmOptions = document.getElementById('jvmOptions').value;
            const mavenThreads = parseInt(document.getElementById('mavenThreads').value);

            setButtonLoading('btnSaveSettings', true);

            try {
                const payload = {
                    group_id: groupId,
                    jvm_options: jvmOptions,
                    maven_profiles: mavenProfiles,
                    maven_threads: mavenThreads
                };

                if (settingsFileContent) {
                    payload.settings_xml_content = settingsFileContent;
                } else if (settingsFileName) {
                    payload.settings_file_name = settingsFileName;
                }

                const response = await fetch('/api/group/settings', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
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

            setButtonLoading('btnLoadProjects', true);
            updateStatus('Loading microservices...');

            const tbody = document.getElementById('servicesTableBody');
            tbody.innerHTML = '<tr><td colspan="3" class="loading-spinner">⏳ Loading microservices...</td></tr>';

            try {
                const response = await fetch(`/api/projects/${groupId}`);
                const data = await response.json();
                projectsData = data.projects.map(project => ({
                    ...project,
                    branches: [],
                    selectedBranch: project.default_branch,
                    branchesLoaded: false,
                    branchesLoading: false
                }));

                if (projectsData.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; padding: 60px; color: #6c757d;"><div style="font-size: 48px; margin-bottom: 16px;">📦</div><div>No projects found in this group</div></td></tr>';
                    updateStatus('No projects found');
                    document.getElementById('projectCount').style.display = 'none';
                    return;
                }

                renderProjectsTable();
                updateStatus(`Loaded ${projectsData.length} microservices`);
                document.getElementById('projectCount').textContent = `${projectsData.length} services`;
                document.getElementById('projectCount').style.display = 'inline-block';
                updateSelectionInfo();
            } catch (error) {
                alert('Error loading projects: ' + error);
                tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; padding: 60px; color: #dc3545;">❌ Error loading projects</td></tr>';
            } finally {
                setButtonLoading('btnLoadProjects', false);
            }
        }

        async function loadBranchesForProject(index) {
            const project = projectsData[index];
            
            if (project.branchesLoaded || project.branchesLoading) {
                return;
            }

            if (branchCache[project.id]) {
                project.branches = branchCache[project.id];
                project.branchesLoaded = true;
                renderBranchSelection(index);
                return;
            }

            project.branchesLoading = true;
            updateBranchCell(index, '⏳ Loading branches...');

            try {
                const response = await fetch(`/api/project/${project.id}/branches`);
                const data = await response.json();
                
                if (data.branches && data.branches.length > 0) {
                    project.branches = data.branches;
                    project.branchesLoaded = true;
                    branchCache[project.id] = data.branches;
                    
                    renderBranchSelection(index);
                } else {
                    updateBranchCell(index, 'No branches found');
                }
            } catch (error) {
                console.error(`Error loading branches for ${project.name}:`, error);
                updateBranchCell(index, '❌ Error loading branches');
            } finally {
                project.branchesLoading = false;
            }
        }

        function updateBranchCell(index, message) {
            const cell = document.querySelector(`#branch-cell-${index}`);
            if (cell) {
                cell.innerHTML = `<div class="branch-loading">${message}</div>`;
            }
        }

        function renderBranchSelection(index) {
            const project = projectsData[index];
            const cell = document.querySelector(`#branch-cell-${index}`);
            if (!cell) return;

            if (project.branches.length === 0) {
                cell.innerHTML = `<div class="no-branches">No branches available</div>`;
                return;
            }

            const searchId = `branch-search-${index}`;
            const selectId = `branch-select-${index}`;
            
            let html = `
                <div class="branch-container">
                    <div class="branch-search-wrapper">
                        <input type="text" 
                               class="branch-search" 
                               id="${searchId}"
                               placeholder="Search ${project.branches.length} branches..."
                               oninput="filterBranches(${index})">
                        <span class="search-icon" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); pointer-events: none;">🔍</span>
                    </div>
                    <select class="branch-select" 
                            id="${selectId}" 
                            size="5" 
                            onchange="handleBranchChange(${index}, this.value)">
            `;

            project.branches.forEach(branch => {
                const isDefault = branch === project.default_branch;
                const selected = branch === project.selectedBranch ? 'selected' : '';
                html += `<option value="${branch}" ${selected} data-branch="${branch.toLowerCase()}" style="padding: 6px;">
                    ${branch}${isDefault ? ' 🌟' : ''}
                </option>`;
            });

            html += `
                    </select>
                    <div class="branch-count">${project.branches.length} branches total</div>
                </div>
            `;

            cell.innerHTML = html;
        }

        function filterBranches(index) {
            const searchInput = document.getElementById(`branch-search-${index}`);
            const select = document.getElementById(`branch-select-${index}`);
            
            if (!searchInput || !select) return;

            const searchTerm = searchInput.value.toLowerCase();
            const options = select.querySelectorAll('option');

            let visibleCount = 0;
            options.forEach(option => {
                const branchName = option.getAttribute('data-branch');
                if (branchName.includes(searchTerm)) {
                    option.style.display = '';
                    visibleCount++;
                } else {
                    option.style.display = 'none';
                }
            });

            const countDiv = select.parentElement.querySelector('.branch-count');
            if (countDiv) {
                if (searchTerm) {
                    countDiv.textContent = `${visibleCount} of ${options.length} branches`;
                } else {
                    countDiv.textContent = `${options.length} branches total`;
                }
            }
        }

        function renderProjectsTable() {
            const tbody = document.getElementById('servicesTableBody');
            tbody.innerHTML = '';

            projectsData.forEach((project, index) => {
                const row = document.createElement('tr');
                
                const checkboxCell = document.createElement('td');
                checkboxCell.innerHTML = `<input type="checkbox" class="service-checkbox" data-index="${index}" onchange="handleServiceCheckboxChange(${index})">`;
                row.appendChild(checkboxCell);

                const nameCell = document.createElement('td');
                nameCell.innerHTML = `<span class="service-name">${project.name}</span>`;
                row.appendChild(nameCell);

                const branchCell = document.createElement('td');
                branchCell.id = `branch-cell-${index}`;
                branchCell.innerHTML = `<div style="font-size: 13px; color: #6c757d;">Select service to load branches</div>`;
                row.appendChild(branchCell);

                tbody.appendChild(row);
            });
        }

        async function handleServiceCheckboxChange(index) {
            const checkbox = document.querySelector(`.service-checkbox[data-index="${index}"]`);
            const project = projectsData[index];
            
            if (checkbox.checked && !project.branchesLoaded && !project.branchesLoading) {
                await loadBranchesForProject(index);
            }

            updateSelectionInfo();
        }

        function handleBranchChange(index, value) {
            projectsData[index].selectedBranch = value;
        }

        function toggleSelectAll() {
            const selectAll = document.getElementById('selectAllCheckbox').checked;
            const checkboxes = document.querySelectorAll('.service-checkbox');
            
            checkboxes.forEach((cb, index) => {
                const row = cb.closest('tr');
                if (row && row.style.display !== 'none') {
                    cb.checked = selectAll;
                    if (selectAll) {
                        handleServiceCheckboxChange(index);
                    }
                }
            });
        }

        function updateSelectionInfo() {
            const checked = document.querySelectorAll('.service-checkbox:checked').length;
            const total = projectsData.length;
            const info = document.getElementById('selectionInfo');
            
            if (checked > 0) {
                info.textContent = `${checked} of ${total} selected`;
            } else {
                info.textContent = '';
            }
        }

        function getSelectedServices() {
            const selected = [];
            const checkboxes = document.querySelectorAll('.service-checkbox:checked');
            
            checkboxes.forEach(checkbox => {
                const index = parseInt(checkbox.dataset.index);
                const project = projectsData[index];
                
                if (!project.branchesLoaded || !project.selectedBranch) {
                    console.warn(`Service ${project.name} selected but branch not loaded`);
                    return;
                }
                
                selected.push({
                    name: project.name,
                    repo_url: project.http_url_to_repo,
                    branch: project.selectedBranch
                });
            });

            return selected;
        }

        async function buildSelected() {
            const selectedServices = getSelectedServices();
            
            if (selectedServices.length === 0) {
                alert('Please select at least one service');
                return;
            }

            const checkboxes = document.querySelectorAll('.service-checkbox:checked');
            let missingBranches = [];
            
            checkboxes.forEach(checkbox => {
                const index = parseInt(checkbox.dataset.index);
                const project = projectsData[index];
                if (!project.branchesLoaded) {
                    missingBranches.push(project.name);
                }
            });

            if (missingBranches.length > 0) {
                alert(`Please wait for branches to load for: ${missingBranches.join(', ')}`);
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

            document.getElementById('selectAllCheckbox').checked = true;
            
            const promises = [];
            for (let i = 0; i < projectsData.length; i++) {
                const checkbox = document.querySelector(`.service-checkbox[data-index="${i}"]`);
                checkbox.checked = true;
                
                if (!projectsData[i].branchesLoaded && !projectsData[i].branchesLoading) {
                    promises.push(loadBranchesForProject(i));
                }
            }

            updateSelectionInfo();
            updateStatus('Loading branches for all services...');
            
            await Promise.all(promises);
            
            updateStatus('All branches loaded. Starting build...');
            
            setTimeout(() => {
                buildSelected();
            }, 500);
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

        // Initialize on load
        window.onload = async function() {
            // Load config
            try {
                const response = await fetch('/api/config');
                const data = await response.json();
                if (data.gitlab_url) {
                    document.getElementById('gitlabUrl').value = data.gitlab_url;
                }
            } catch (error) {
                console.error('Error loading config:', error);
            }
            
            // Check for saved credentials
            const savedCreds = loadCredentialsFromStorage();
            if (savedCreds) {
                document.getElementById('gitlabUrl').value = savedCreds.url;
                document.getElementById('privateToken').value = savedCreds.token;
                showSavedCredentials();
                
                // Auto-connect
                await connectGitLab();
            }
            
            // Load settings files
            await refreshSettingsFiles();
            
            updateStatus('Ready to connect');
        };
    </script>
</body>
</html>
"""