#!/usr/bin/env python3
"""
Microservice Build Automation Tool - Main Entry Point
High-performance parallel builds with intelligent caching
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.utils.system_info import SystemInfo


def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("🚀 Microservice Build Automation Tool - Enhanced Edition")
    print("=" * 80)

    # Display system information
    sys_info = SystemInfo()
    print(f"\n💻 System Configuration:")
    print(f"   • CPU Cores: {sys_info.cpu_count} (Logical: {sys_info.cpu_logical_count})")
    print(f"   • Available RAM: {sys_info.available_memory_gb:.1f} GB / {sys_info.total_memory_gb:.1f} GB")
    print(f"   • Recommended parallel builds: {sys_info.recommended_workers}")
    print(f"   • OS: {sys_info.os_name}")

    print("\n🔧 Features:")
    print("   • Multi-branch support with auto-detection")
    print("   • Smart repository caching (pull if exists, clone if new)")
    print("   • Maximum parallelization based on system resources")
    print("   • Multi-threaded Maven builds with optimized JVM settings")
    print("   • Settings file management (config/ folder)")
    print("   • Copy logs functionality")
    print("   • Real-time build monitoring")

    print("\n📡 Starting web server...")
    print("🌐 Open your browser: http://localhost:5000")
    print("\n⚠️  Press Ctrl+C to stop\n")
    print("=" * 80 + "\n")

    app, socketio = create_app()
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()