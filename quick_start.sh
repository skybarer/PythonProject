#!/bin/bash
# Quick Start Script for Microservice Build Automation
# This script automates the entire setup process

set - e  # Exit on any error

echo
"=============================================="
echo
"🚀 Microservice Build Automation Setup"
echo
"=============================================="
echo
""

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

# Function to print colored output
print_success()
{
    echo - e
"${GREEN}✅ $1${NC}"
}

print_error()
{
    echo - e
"${RED}❌ $1${NC}"
}

print_warning()
{
    echo - e
"${YELLOW}⚠️  $1${NC}"
}

print_info()
{
    echo - e
"ℹ️  $1"
}

# Check Python version
echo
"Checking Python version..."
if command - v python3 & > / dev / null; then
PYTHON_CMD = python3
PYTHON_VERSION =$(python3 - -version 2 > & 1 | awk '{print $2}')
print_success
"Python found: $PYTHON_VERSION"
elif command - v
python & > / dev / null;
then
PYTHON_CMD = python
PYTHON_VERSION =$(python - -version 2 > & 1 | awk '{print $2}')
print_success
"Python found: $PYTHON_VERSION"
else
print_error
"Python not found. Please install Python 3.7+"
exit
1
fi

# Check pip
echo
""
echo
"Checking pip..."
if command - v pip3 & > / dev / null; then
PIP_CMD = pip3
print_success
"pip3 found"
elif command - v
pip & > / dev / null;
then
PIP_CMD = pip
print_success
"pip found"
else
print_error
"pip not found. Please install pip"
exit
1
fi

# Create directory structure
echo
""
echo
"Creating directory structure..."
mkdir - p
app / services
mkdir - p
app / utils
mkdir - p
config / settings
mkdir - p
workspace
mkdir - p.build_cache
print_success
"Directories created"

# Create __init__.py files
echo
""
echo
"Creating package files..."
touch
app / __init__.py
touch
app / services / __init__.py
touch
app / utils / __init__.py
print_success
"Package files created"

# Check if required files exist
echo
""
echo
"Checking required files..."

REQUIRED_FILES = (
    "main.py"
    "requirements.txt"
    "app/__init__.py"
    "app/config.py"
    "app/routes.py"
    "app/templates.py"
    "app/services/builder.py"
    "app/services/build_cache.py"
    "app/services/command_finder.py"
    "app/services/config_manager.py"
    "app/services/git_service.py"
    "app/services/gitlab_client.py"
    "app/utils/system_info.py"
)

MISSING_FILES = ()

for file in "${REQUIRED_FILES[@]}"; do
if [-f "$file"]; then
print_success
"Found: $file"
else
print_error
"Missing: $file"
MISSING_FILES += ("$file")
fi
done

if [ ${  # MISSING_FILES[@]} -ne 0 ]; then
echo ""
print_error "Missing ${#MISSING_FILES[@]} required file(s):"
for file in "${MISSING_FILES[@]}"; do
echo "  - $file"
done
echo ""
print_warning "Please ensure all files are in place before continuing"
exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
if[-f "requirements.txt"]; then
$PIP_CMD install -r requirements.txt
print_success "Dependencies installed"
else
print_error "requirements.txt not found"
exit 1
fi

# Verify installations
echo ""
echo "Verifying installations..."

REQUIRED_PACKAGES=("flask" "flask_socketio" "requests" "psutil")
ALL_INSTALLED=true

for package in "${REQUIRED_PACKAGES[@]}"; do
if $PYTHON_CMD -c "import $package" 2 > / dev / null; then
print_success "$package installed"
else
print_error "$package not installed"
ALL_INSTALLED=false
fi
done

if["$ALL_INSTALLED" = false]; then
print_error "Some packages failed to install"
exit 1
fi

# Create sample settings.xml if it doesn't exist
echo ""
echo "Creating sample settings.xml..."
SAMPLE_SETTINGS="config/settings/sample_settings.xml"

if[! -f "$SAMPLE_SETTINGS"]; then
cat > "$SAMPLE_SETTINGS" << 'EOF'
< ?xml version="1.0" encoding="UTF-8"? >
< settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"
xsi: schemaLocation = "http://maven.apache.org/SETTINGS/1.0.0
http: // maven.apache.org / xsd / settings - 1.0
.0.xsd
">
< localRepository >${user.home} /.m2 / repository < / localRepository >

                                                      < mirrors >
                                                      < mirror >
                                                      < id > central < / id >
                                                                         < mirrorOf > central < / mirrorOf >
                                                                                                  < url > https: // repo.maven.apache.org / maven2 < / url >
                                                                                                                                                       < / mirror >
                                                                                                                                                           < / mirrors >

                                                                                                                                                               < profiles >
                                                                                                                                                               < profile >
                                                                                                                                                               < id > dev < / id >
                                                                                                                                                                              < properties >
                                                                                                                                                                              < environment > development < / environment >
                                                                                                                                                                                                              < / properties >
                                                                                                                                                                                                                  < / profile >
                                                                                                                                                                                                                      < / profiles >
                                                                                                                                                                                                                          < / settings >
                                                                                                                                                                                                                              EOF
print_success
"Sample settings.xml created"
else
print_info
"Sample settings.xml already exists"
fi

# Test imports
echo
""
echo
"Testing Python imports..."

if $PYTHON_CMD - c
"from app.services.git_service import GitService"
2 > / dev / null;
then
print_success
"GitService import OK"
else
print_error
"GitService import failed"
exit
1
fi

if $PYTHON_CMD - c
"from app.services.builder import MicroserviceBuilder"
2 > / dev / null;
then
print_success
"MicroserviceBuilder import OK"
else
print_error
"MicroserviceBuilder import failed"
exit
1
fi

if $PYTHON_CMD - c
"from app.routes import register_routes"
2 > / dev / null;
then
print_success
"Routes import OK"
else
print_error
"Routes import failed"
exit
1
fi

# Check for Git
echo
""
echo
"Checking system prerequisites..."

if command - v
git & > / dev / null;
then
GIT_VERSION =$(git - -version)
print_success
"Git: $GIT_VERSION"
else
print_warning
"Git not found in PATH"
print_info
"You can set the path manually in the UI"
fi

# Check for Maven
if command - v
mvn & > / dev / null;
then
MAVEN_VERSION =$(mvn - -version | head - n 1)
print_success
"Maven: $MAVEN_VERSION"
else
print_warning
"Maven not found in PATH"
print_info
"You can set the path manually in the UI"
fi

# Final summary
echo
""
echo
"=============================================="
echo
"✅ Setup Complete!"
echo
"=============================================="
echo
""
print_info
"Next steps:"
echo
"  1. Add your Maven settings.xml files to: config/settings/"
echo
"  2. Start the application: $PYTHON_CMD main.py"
echo
"  3. Open your browser: http://localhost:5000"
echo
""

# Offer to start the application
read - p
"Do you want to start the application now? (y/n) " - n
1 - r
echo
""

if [[ $REPLY = ~ ^ [Yy]$]]; then
echo
""
echo
"Starting application..."
echo
"Press Ctrl+C to stop"
echo
""
$PYTHON_CMD
main.py
fi