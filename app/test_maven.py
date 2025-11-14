"""
Complete System Test - Tests Git and Maven execution
This simulates exactly what the builder does
"""

import subprocess
import sys
import os
from pathlib import Path

def test_command_execution(command_name, command_path):
    """Test different execution methods for a command"""
    print(f"\n{'='*70}")
    print(f"Testing {command_name}: {command_path}")
    print('='*70)

    is_windows = sys.platform.startswith('win')
    success_methods = []

    # Method 1: Direct with shell=True
    print(f"\n[Method 1] Direct execution with shell=True")
    print("-" * 70)
    try:
        cmd_str = f'"{command_path}" --version'
        print(f"Command: {cmd_str}")

        result = subprocess.run(
            cmd_str,
            capture_output=True,
            text=True,
            timeout=10,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW if is_windows else 0
        )

        if result.returncode == 0:
            print(f"✅ SUCCESS")
            print(f"Output: {result.stdout.split(chr(10))[0]}")
            success_methods.append("Method 1: shell=True")
        else:
            print(f"❌ FAILED (return code: {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    # Method 2: cmd.exe /c (Windows only)
    if is_windows:
        print(f"\n[Method 2] Using cmd.exe /c")
        print("-" * 70)
        try:
            full_cmd = f'cmd.exe /c ""{command_path}" --version"'
            print(f"Command: {full_cmd}")

            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=10,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                print(f"✅ SUCCESS")
                print(f"Output: {result.stdout.split(chr(10))[0]}")
                success_methods.append("Method 2: cmd.exe /c")
            else:
                print(f"❌ FAILED (return code: {result.returncode})")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}")
        except Exception as e:
            print(f"❌ ERROR: {e}")

    # Method 3: Direct without shell (list args)
    print(f"\n[Method 3] Direct execution without shell (list args)")
    print("-" * 70)
    try:
        print(f"Command: [{command_path}, '--version']")

        result = subprocess.run(
            [command_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW if is_windows else 0
        )

        if result.returncode == 0:
            print(f"✅ SUCCESS")
            print(f"Output: {result.stdout.split(chr(10))[0]}")
            success_methods.append("Method 3: shell=False with list")
        else:
            print(f"❌ FAILED (return code: {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
    except FileNotFoundError:
        print(f"❌ FileNotFoundError - Command not found in PATH")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    return success_methods

def find_maven():
    """Find Maven installation"""
    is_windows = sys.platform.startswith('win')

    # Try PATH first
    commands = ["mvn.cmd", "mvn"] if is_windows else ["mvn"]

    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=is_windows
            )
            if result.returncode == 0:
                return cmd
        except:
            pass

    # Search common paths on Windows
    if is_windows:
        user_home = Path.home()
        search_paths = [
            user_home / "Documents" / "software",
            Path("C:/Program Files/Apache/Maven"),
            Path("C:/Program Files/Maven"),
            Path("C:/Maven"),
            user_home / "apache-maven",
            Path("D:/Maven"),
        ]

        for base in search_paths:
            if base.exists():
                try:
                    for item in base.iterdir():
                        if item.is_dir() and 'maven' in item.name.lower():
                            maven_bin = item / "bin" / "mvn.cmd"
                            if maven_bin.exists():
                                return str(maven_bin.resolve())
                except:
                    pass

    return None

def find_git():
    """Find Git installation"""
    is_windows = sys.platform.startswith('win')
    commands = ["git.exe", "git"] if is_windows else ["git"]

    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=is_windows
            )
            if result.returncode == 0:
                return cmd
        except:
            pass

    return None

def main():
    print("="*70)
    print("COMPLETE SYSTEM TEST")
    print("="*70)

    is_windows = sys.platform.startswith('win')
    print(f"\nPlatform: {'Windows' if is_windows else 'Unix/Linux/Mac'}")
    print(f"Python: {sys.version}")

    # Test Git
    print("\n" + "="*70)
    print("TESTING GIT")
    print("="*70)

    git_cmd = find_git()
    if git_cmd:
        print(f"✅ Found Git: {git_cmd}")
        git_methods = test_command_execution("Git", git_cmd)

        if git_methods:
            print(f"\n✅ Git working methods: {', '.join(git_methods)}")
        else:
            print(f"\n❌ Git found but NO execution method works!")
    else:
        print("❌ Git not found")

    # Test Maven
    print("\n" + "="*70)
    print("TESTING MAVEN")
    print("="*70)

    maven_cmd = find_maven()
    if maven_cmd:
        print(f"✅ Found Maven: {maven_cmd}")
        maven_methods = test_command_execution("Maven", maven_cmd)

        if maven_methods:
            print(f"\n✅ Maven working methods: {', '.join(maven_methods)}")
        else:
            print(f"\n❌ Maven found but NO execution method works!")
            print("\nPossible issues:")
            print("1. JAVA_HOME not set")
            print("2. Java not in PATH")
            print("3. Incorrect Maven installation")
            print("\nTry in Command Prompt:")
            print(f'   "{maven_cmd}" --version')
    else:
        print("❌ Maven not found")

    # Test Java (Maven requirement)
    print("\n" + "="*70)
    print("TESTING JAVA (Maven requirement)")
    print("="*70)

    try:
        result = subprocess.run(
            "java -version",
            capture_output=True,
            text=True,
            timeout=5,
            shell=True
        )

        if result.returncode == 0:
            # Java outputs to stderr
            output = result.stderr if result.stderr else result.stdout
            print(f"✅ Java found")
            print(f"Version: {output.split(chr(10))[0]}")
        else:
            print(f"❌ Java not working properly")
    except Exception as e:
        print(f"❌ Java test failed: {e}")
        print("\n⚠️  Maven requires Java to be installed and in PATH")
        print("   Download Java from: https://adoptium.net/")

    # Environment check
    print("\n" + "="*70)
    print("ENVIRONMENT VARIABLES")
    print("="*70)

    important_vars = ['JAVA_HOME', 'MAVEN_HOME', 'PATH']
    for var in important_vars:
        value = os.environ.get(var, 'NOT SET')
        if var == 'PATH':
            print(f"\n{var}:")
            for path in value.split(os.pathsep)[:10]:
                print(f"  - {path}")
            if len(value.split(os.pathsep)) > 10:
                print(f"  ... and {len(value.split(os.pathsep)) - 10} more")
        else:
            print(f"{var}: {value}")

    # Final recommendation
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)

    if maven_cmd and git_cmd:
        print("✅ Both Git and Maven are available!")
        print("\nThe builder will use:")
        print(f"  Git: {git_cmd}")
        print(f"  Maven: {maven_cmd}")
        print(f"  Execution method: cmd.exe /c (most reliable on Windows)")
    else:
        print("❌ Setup incomplete")
        if not git_cmd:
            print("  - Install Git: https://git-scm.com/downloads")
        if not maven_cmd:
            print("  - Install Maven: https://maven.apache.org/download.cgi")
            print("  - Set JAVA_HOME environment variable")

if __name__ == "__main__":
    main()