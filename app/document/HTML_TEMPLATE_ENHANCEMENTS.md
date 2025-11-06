# HTML Template Enhancements

Create `app/templates.py` with an enhanced HTML template. Key additions to the original template:

## New UI Components

### 1. System Information Panel (Add after Prerequisites section)

```html
<div class="section">
    <h2>💻 System Information</h2>
    <button class="btn btn-info" onclick="loadSystemInfo()">Load System Info</button>
    <div id="systemInfo" class="system-info" style="display: none;">
        <div class="info-grid">
            <div class="info-item">
                <strong>CPU Cores:</strong> <span id="cpuCores"></span>
            </div>
            <div class="info-item">
                <strong>Logical Cores:</strong> <span id="cpuLogical"></span>
            </div>
            <div class="info-item">
                <strong>Available RAM:</strong> <span id="availableRam"></span>
            </div>
            <div class="info-item">
                <strong>Recommended Workers:</strong> <span id="recWorkers"></span>
            </div>
            <div class="info-item">
                <strong>Maven Threads:</strong> <span id="mavenThreads"></span>
            </div>
            <div class="info-item">
                <strong>Optimized JVM:</strong> <span id="jvmOpts" style="font-size: 11px;"></span>
            </div>
        </div>
    </div>
</div>
```

### 2. Settings File Dropdown (Replace file upload in Group Configuration)

```html
<div class="form-group">
    <label>Maven Settings File</label>
    <select id="settingsFileDropdown" onchange="handleSettingsSelection()">
        <option value="">-- Select existing or upload new --</option>
    </select>
    <button class="btn btn-secondary" onclick="showFileUpload()">Upload New</button>
    
    <div id="fileUploadSection" style="display: none; margin-top: 10px;">
        <div class="file-upload-area" id="fileUploadArea" onclick="document.getElementById('settingsFile').click()">
            <div>📄 Click or drag to upload settings.xml</div>
            <input type="file" id="settingsFile" accept=".xml" style="display: none;" onchange="handleFileSelect(event)">
        </div>
        <div id="fileInfo" class="file-info" style="display: none;"></div>
    </div>
</div>
```

### 3. Branch Selection for Each Service (Modify services list)

```html
<div class="form-group">
    <label>Services & Branches</label>
    <div id="servicesList"></div>
</div>

<style>
.service-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    margin-bottom: 8px;
    border-radius: 4px;
    border: 1px solid #ddd;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
}

.service-item:hover {
    background: #f8f9fa;
    border-color: #667eea;
}

.service-item.selected {
    background: #e7f3ff;
    border-color: #667eea;
}

.service-name {
    flex: 1;
    font-weight: 500;
}

.branch-select {
    margin-left: 10px;
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 13px;
    min-width: 150px;
}

.checkbox {
    margin-right: 10px;
}
</style>
```

### 4. Copy Logs Button (Add to Build Log section)

```html
<div class="section">
    <h2>Build Log</h2>
    <div style="margin-bottom: 10px;">
        <button class="btn btn-info" onclick="copyLogs()">📋 Copy Logs</button>
        <button class="btn btn-secondary" onclick="exportLogs()">💾 Export Logs</button>
        <button class="btn btn-secondary" onclick="clearLogs()">🗑️ Clear Logs</button>
    </div>
    <div id="logOutput"></div>
</div>
```

### 5. Build Progress Indicator (Add before log output)

```html
<div id="buildProgress" style="display: none; margin-bottom: 15px;">
    <div class="progress-bar">
        <div class="progress-fill" id="progressFill"></div>
    </div>
    <div class="progress-text">
        Building <span id="currentService"></span>... 
        (<span id="completedCount">0</span>/<span id="totalCount">0</span>)
    </div>
</div>

<style>
.progress-bar {
    width: 100%;
    height: 20px;
    background: #f0f0f0;
    border-radius: 10px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    width: 0%;
    transition: width 0.3s ease;
}

.progress-text {
    margin-top: 8px;
    text-align: center;
    font-size: 14px;
    color: #666;
}
</style>
```

## Enhanced JavaScript Functions

### 1. Load System Information

```javascript
async function loadSystemInfo() {
    try {
        const response = await fetch('/api/system-info');
        const data = await response.json();
        
        document.getElementById('cpuCores').textContent = data.cpu_cores;
        document.getElementById('cpuLogical').textContent = data.cpu_logical_cores;
        document.getElementById('availableRam').textContent = 
            `${data.available_memory_gb} GB / ${data.total_memory_gb} GB`;
        document.getElementById('recWorkers').textContent = data.recommended_workers;
        document.getElementById('mavenThreads').textContent = data.recommended_maven_threads;
        document.getElementById('jvmOpts').textContent = data.optimized_maven_opts;
        
        document.getElementById('systemInfo').style.display = 'block';
        
        // Auto-set optimal values
        document.getElementById('maxWorkers').value = data.recommended_workers;
        if (!document.getElementById('jvmOptions').value) {
            document.getElementById('jvmOptions').value = data.optimized_maven_opts;
        }
    } catch (error) {
        alert('Error loading system info: ' + error);
    }
}
```

### 2. Load Settings Files Dropdown

```javascript
async function loadSettingsFiles() {
    try {
        const response = await fetch('/api/settings-files');
        const data = await response.json();
        
        const dropdown = document.getElementById('settingsFileDropdown');
        dropdown.innerHTML = '<option value="">-- Select existing or upload new --</option>';
        
        data.files.forEach(file => {
            const option = document.createElement('option');
            option.value = file.name;
            option.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading settings files:', error);
    }
}

function handleSettingsSelection() {
    const selected = document.getElementById('settingsFileDropdown').value;
    if (selected) {
        document.getElementById('fileUploadSection').style.display = 'none';
    }
}

function showFileUpload() {
    document.getElementById('fileUploadSection').style.display = 'block';
    document.getElementById('settingsFileDropdown').value = '';
}
```

### 3. Enhanced Load Projects with Branches

```javascript
async function loadProjects() {
    const groupId = document.getElementById('groupSelect').value;
    if (!groupId) {
        alert('Please select a group first');
        return;
    }
    
    updateStatus('Loading projects...');
    
    try {
        const response = await fetch(`/api/projects/${groupId}`);
        const data = await response.json();
        
        const servicesList = document.getElementById('servicesList');
        servicesList.innerHTML = '';
        selectedServices.clear();
        projectBranches = {};  // Store branch selections
        
        for (const project of data.projects) {
            // Fetch branches for each project
            const branchesResp = await fetch(`/api/project/${project.id}/branches`);
            const branchesData = await branchesResp.json();
            
            const div = document.createElement('div');
            div.className = 'service-item';
            div.dataset.projectId = project.id;
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'checkbox';
            checkbox.onchange = () => toggleService(project, div);
            
            const nameSpan = document.createElement('span');
            nameSpan.className = 'service-name';
            nameSpan.textContent = project.name;
            
            const branchSelect = document.createElement('select');
            branchSelect.className = 'branch-select';
            branchSelect.onclick = (e) => e.stopPropagation();
            
            branchesData.branches.forEach(branch => {
                const option = document.createElement('option');
                option.value = branch;
                option.textContent = branch;
                if (branch === 'master' || branch === 'main') {
                    option.selected = true;
                }
                branchSelect.appendChild(option);
            });
            
            branchSelect.onchange = () => {
                projectBranches[project.id] = {
                    name: project.name,
                    repo_url: project.http_url_to_repo,
                    branch: branchSelect.value
                };
            };
            
            // Set default branch
            const defaultBranch = project.default_branch || 'master';
            branchSelect.value = defaultBranch;
            projectBranches[project.id] = {
                name: project.name,
                repo_url: project.http_url_to_repo,
                branch: defaultBranch
            };
            
            div.appendChild(checkbox);
            div.appendChild(nameSpan);
            div.appendChild(branchSelect);
            servicesList.appendChild(div);
        }
        
        updateStatus(`Loaded ${data.projects.length} projects`);
    } catch (error) {
        alert('Error loading projects: ' + error);
    }
}

function toggleService(project, element) {
    const checkbox = element.querySelector('.checkbox');
    checkbox.checked = !checkbox.checked;
    
    if (checkbox.checked) {
        selectedServices.add(project.id);
        element.classList.add('selected');
    } else {
        selectedServices.delete(project.id);
        element.classList.remove('selected');
    }
}
```

### 4. Copy and Export Logs

```javascript
function copyLogs() {
    const logOutput = document.getElementById('logOutput');
    const text = logOutput.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = updateStatus('Logs copied to clipboard!');
        setTimeout(() => updateStatus('Ready'), 2000);
    }).catch(err => {
        alert('Failed to copy logs: ' + err);
    });
}

function exportLogs() {
    const logOutput = document.getElementById('logOutput');
    const text = logOutput.innerText;
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `build-logs-${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}
```

### 5. Enhanced Build with Progress

```javascript
async function buildSelected() {
    if (selectedServices.size === 0) {
        alert('Please select at least one service');
        return;
    }
    
    const groupId = document.getElementById('groupSelect').value;
    const force = document.getElementById('forceRebuild').checked;
    const maxWorkers = parseInt(document.getElementById('maxWorkers').value);
    
    // Prepare build configs with branches
    const buildConfigs = Array.from(selectedServices).map(projectId => projectBranches[projectId]);
    
    document.getElementById('logOutput').innerHTML = '';
    document.getElementById('buildProgress').style.display = 'block';
    document.getElementById('totalCount').textContent = selectedServices.size;
    document.getElementById('completedCount').textContent = 0;
    
    updateStatus(`Building ${selectedServices.size} services...`);
    
    try {
        const response = await fetch('/api/build', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                group_id: groupId,
                build_configs: buildConfigs,
                force: force,
                max_workers: maxWorkers
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            updateStatus(data.message);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error starting build: ' + error);
    }
}
```

## Call on Page Load

```javascript
window.onload = function() {
    loadSystemInfo();  // Auto-load system info
    loadSettingsFiles();  // Load settings dropdown
    
    // Load saved configuration
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            if (data.gitlab_url) {
                document.getElementById('gitlabUrl').value = data.gitlab_url;
            }
        })
        .catch(error => console.error('Error loading config:', error));
};
```

This enhanced template provides:
- Real-time system monitoring
- Settings file management
- Per-service branch selection
- Build progress tracking
- Log export functionality
- Better UX with visual feedback