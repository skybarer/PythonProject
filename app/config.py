"""
Application configuration
"""

import os
from pathlib import Path


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'microservice-build-automation-secret'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Directories
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_DIR = BASE_DIR / 'config'
    WORKSPACE_DIR = BASE_DIR / 'workspace'
    CACHE_DIR = BASE_DIR / '.build_cache'
    SETTINGS_DIR = CONFIG_DIR / 'settings'

    # Build settings
    DEFAULT_MAX_WORKERS = 4
    DEFAULT_JVM_OPTIONS = '-Xmx4G -XX:+UseParallelGC -XX:ParallelGCThreads=4'
    BUILD_TIMEOUT = 1800  # 30 minutes
    GIT_TIMEOUT = 600  # 10 minutes

    # Maven optimization
    MAVEN_OPTS_TEMPLATE = '-Xmx{memory}G -XX:+UseParallelGC -XX:ParallelGCThreads={threads} -Dmaven.artifact.threads={threads}'