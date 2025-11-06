#!/usr/bin/env python3
"""
Quick setup script for Microservice Build Automation
"""

import os
import sys
from pathlib import Path


def create_directory_structure():
    """Create required directories"""
    dirs = [
        'app/services',
        'app/utils',
        'config/settings',
        'workspace',
        '.build_cache'
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

        # Create __init__.py for Python packages
        if 'app/' in dir_path:
            init_file = Path(dir_path) / '__init__.py'
            if not init_file.exists():
                init_file.touch()

    print("✅ Directory structure created")


def create_init_files():
    """Create __init__.py files"""
    init_files = [
        'app/__init__.py',
        'app/services/__init__.py',
        'app/utils/__init__.py'
    ]

    for init_file in init_files:
        path = Path(init_file)
        if not path.exists():
            path.touch()

    print("✅ Package files created")


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'flask',
        'flask_socketio',
        'requests',
        'psutil'
    ]

    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ All dependencies installed")
    return True


def create_sample_settings():
    """Create sample settings.xml"""
    settings_path = Path('config/settings/sample_settings.xml')

    if not settings_path.exists():
        sample_content = '''<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
                              http://maven.apache.org/xsd/settings-1.0.0.xsd">
    <localRepository>${user.home}/.m2/repository</localRepository>

    <mirrors>
        <mirror>
            <id>central</id>
            <mirrorOf>central</mirrorOf>
            <url>https://repo.maven.apache.org/maven2</url>
        </mirror>
    </mirrors>

    <profiles>
        <profile>
            <id>dev</id>
            <properties>
                <environment>development</environment>
            </properties>
        </profile>
    </profiles>
</settings>'''

        settings_path.write_text(sample_content)
        print(f"✅ Sample settings.xml created at {settings_path}")


def main():
    print("\n" + "=" * 60)
    print("🚀 Microservice Build Automation - Setup")
    print("=" * 60 + "\n")

    create_directory_structure()
    create_init_files()
    create_sample_settings()

    print("\n" + "=" * 60)
    print("Checking dependencies...")
    print("=" * 60 + "\n")

    if not check_dependencies():
        print("\n⚠️  Please install dependencies first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Add your Maven settings.xml files to config/settings/")
    print("2. Run: python main.py")
    print("3. Open: http://localhost:5000")
    print("\n" + "=" * 60 + "\n")


if __name__ == '__main__':
    main()