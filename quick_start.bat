@echo off
REM Quick Start Script for Microservice Build Automation (Windows)
REM This script automates the entire setup process

setlocal enabledelayedexpansion

echo ==============================================
echo 🚀 Microservice Build Automation Setup
echo ==============================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo ✅ Python found
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
        echo ✅ Python3 found
    ) else (
        echo ❌ Python not found. Please install Python 3.7+
        pause
        exit /b 1
    )
)

REM Check pip
echo.
echo Checking pip...
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    set PIP_CMD=pip
    echo ✅ pip found
) else (
    pip3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PIP_CMD=pip3
        echo ✅ pip3 found
    ) else (
        echo ❌ pip not found. Please install pip
        pause
        exit /b 1
    )
)

REM Create directory structure
echo.
echo Creating directory structure...
if not exist "app\services" mkdir app\services
if not exist "app\utils" mkdir app\utils
if not exist "config\settings" mkdir config\settings
if not exist "workspace" mkdir workspace
if not exist ".build_cache" mkdir .build_cache
echo ✅ Directories created

REM Create __init__.py files
echo.
echo Creating package files...
type nul > app\__init__.py
type nul > app\services\__init__.py
type nul > app\utils\__init__.py
echo ✅ Package files created

REM Check required files
echo.
echo Checking required files...

set MISSING_COUNT=0

if exist "main.py" (echo ✅ Found: main.py) else (echo ❌ Missing: main.py & set /a MISSING_COUNT+=1)
if exist "requirements.txt" (echo ✅ Found: requirements.txt) else (echo ❌ Missing: requirements.txt & set /a MISSING_COUNT+=1)
if exist "app\config.py" (echo ✅ Found: app\config.py) else (echo ❌ Missing: app\config.py & set /a MISSING_COUNT+=1)
if exist "app\routes.py" (echo ✅ Found: app\routes.py) else (echo ❌ Missing: app\routes.py & set /a MISSING_COUNT+=1)
if exist "app\templates.py" (echo ✅ Found: app\templates.py) else (echo ❌ Missing: app\templates.py & set /a MISSING_COUNT+=1)
if exist "app\services\builder.py" (echo ✅ Found: app\services\builder.py) else (echo ❌ Missing: app\services\builder.py & set /a MISSING_COUNT+=1)
if exist "app\services\build_cache.py" (echo ✅ Found: app\services\build_cache.py) else (echo ❌ Missing: app\services\build_cache.py & set /a MISSING_COUNT+=1)
if exist "app\services\command_finder.py" (echo ✅ Found: app\services\command_finder.py) else (echo ❌ Missing: app\services\command_finder.py & set /a MISSING_COUNT+=1)
if exist "app\services\config_manager.py" (echo ✅ Found: app\services\config_manager.py) else (echo ❌ Missing: app\services\config_manager.py & set /a MISSING_COUNT+=1)
if exist "app\services\git_service.py" (echo ✅ Found: app\services\git_service.py) else (echo ❌ Missing: app\services\git_service.py & set /a MISSING_COUNT+=1)
if exist "app\services\gitlab_client.py" (echo ✅ Found: app\services\gitlab_client.py) else (echo ❌ Missing: app\services\gitlab_client.py & set /a MISSING_COUNT+=1)
if exist "app\utils\system_info.py" (echo ✅ Found: app\utils\system_info.py) else (echo ❌ Missing: app\utils\system_info.py & set /a MISSING_COUNT+=1)

if !MISSING_COUNT! gtr 0 (
    echo.
    echo ❌ Missing !MISSING_COUNT! required files
    echo Please ensure all files are in place before continuing
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo Installing dependencies...
%PIP_CMD% install -r requirements.txt
if %errorlevel% equ 0 (
    echo ✅ Dependencies installed
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Verify installations
echo.
echo Verifying installations...
%PYTHON_CMD% -c "import flask" 2>nul
if %errorlevel% equ 0 (echo ✅ flask installed) else (echo ❌ flask not installed)

%PYTHON_CMD% -c "import flask_socketio" 2>nul
if %errorlevel% equ 0 (echo ✅ flask_socketio installed) else (echo ❌ flask_socketio not installed)

%PYTHON_CMD% -c "import requests" 2>nul
if %errorlevel% equ 0 (echo ✅ requests installed) else (echo ❌ requests not installed)

%PYTHON_CMD% -c "import psutil" 2>nul
if %errorlevel% equ 0 (echo ✅ psutil installed) else (echo ❌ psutil not installed)

REM Create sample settings.xml
echo.
echo Creating sample settings.xml...
if not exist "config\settings\sample_settings.xml" (
    (
        echo ^<?xml version="1.0" encoding="UTF-8"?^>
        echo ^<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
        echo           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        echo           xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
        echo                               http://maven.apache.org/xsd/settings-1.0.0.xsd"^>
        echo     ^<localRepository^>${user.home}/.m2/repository^</localRepository^>
        echo     ^<mirrors^>
        echo         ^<mirror^>
        echo             ^<id^>central^</id^>
        echo             ^<mirrorOf^>central^</mirrorOf^>
        echo             ^<url^>https://repo.maven.apache.org/maven2^</url^>
        echo         ^</mirror^>
        echo     ^</mirrors^>
        echo ^</settings^>
    ) > "config\settings\sample_settings.xml"
    echo ✅ Sample settings.xml created
) else (
    echo ℹ️  Sample settings.xml already exists
)

REM Test imports
echo.
echo Testing Python imports...

%PYTHON_CMD% -c "from app.services.git_service import GitService" 2>nul
if %errorlevel% equ 0 (
    echo ✅ GitService import OK
) else (
    echo ❌ GitService import failed
    pause
    exit /b 1
)

%PYTHON_CMD% -c "from app.services.builder import MicroserviceBuilder" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MicroserviceBuilder import OK
) else (
    echo ❌ MicroserviceBuilder import failed
    pause
    exit /b 1
)

%PYTHON_CMD% -c "from app.routes import register_routes" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Routes import OK
) else (
    echo ❌ Routes import failed
    pause
    exit /b 1
)

REM Check system prerequisites
echo.
echo Checking system prerequisites...

git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git found
) else (
    echo ⚠️  Git not found in PATH
    echo ℹ️  You can set the path manually in the UI
)

mvn --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Maven found
) else (
    echo ⚠️  Maven not found in PATH
    echo ℹ️  You can set the path manually in the UI
)

REM Final summary
echo.
echo ==============================================
echo ✅ Setup Complete!
echo ==============================================
echo.
echo ℹ️  Next steps:
echo   1. Add your Maven settings.xml files to: config\settings\
echo   2. Start the application: %PYTHON_CMD% main.py
echo   3. Open your browser: http://localhost:5000
echo.

REM Offer to start the application
set /p START_NOW="Do you want to start the application now? (y/n): "
if /i "%START_NOW%"=="y" (
    echo.
    echo Starting application...
    echo Press Ctrl+C to stop
    echo.
    %PYTHON_CMD% main.py
)

pause