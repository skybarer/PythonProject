"""
Maven Diagnostic Tool
Run this to verify Maven detection and execution
Usage: python test_maven.py
"""

import subprocess
import sys
from pathlib import Path


def test_maven_detection():
    print("=" * 70)
    print("MAVEN DIAGNOSTIC TOOL")
    print("=" * 70)

    is_windows = sys.platform.startswith('win')
    print(f"\nPlatform: {'Windows' if is_windows else 'Unix/Linux/Mac'}")

    # Test 1: Maven in PATH
    print("\n[Test 1] Maven in PATH")
    print("-" * 70)

    maven_commands = ["mvn.cmd", "mvn"] if is_windows else ["mvn"]

    for cmd in maven_commands:
        try:
            print(f"Testing: {cmd}")
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=is_windows
            )
            if result.returncode == 0:
                print(f"✅ SUCCESS: {cmd}")
                print(f"   Version: {result.stdout.split(chr(10))[0]}")
                print(f"   Command works: {cmd}")
                return cmd
            else:
                print(f"❌ FAILED: {cmd} (return code: {result.returncode})")
        except FileNotFoundError:
            print(f"❌ NOT FOUND: {cmd}")
        except Exception as e:
            print(f"❌ ERROR: {cmd} - {e}")

    # Test 2: Common installation paths (Windows only)
    if is_windows:
        print("\n[Test 2] Searching common installation paths")
        print("-" * 70)

        user_home = Path.home()
        common_paths = [
            user_home / "Documents" / "software",
            Path("C:/Program Files/Apache/Maven"),
            Path("C:/Program Files/Maven"),
            Path("C:/Maven"),
            user_home / "apache-maven",
            Path("D:/Maven"),
            Path("D:/apache-maven"),
        ]

        found_paths = []
        for base_path in common_paths:
            if base_path.exists():
                print(f"Searching: {base_path}")
                try:
                    for item in base_path.iterdir():
                        if item.is_dir() and 'maven' in item.name.lower():
                            maven_bin = item / "bin" / "mvn.cmd"
                            if maven_bin.exists():
                                found_paths.append(str(maven_bin.resolve()))
                                print(f"  ✅ Found: {maven_bin}")
                except PermissionError:
                    print(f"  ⚠️  Permission denied")
                    continue

        # Test found paths
        if found_paths:
            print("\n[Test 3] Testing found Maven installations")
            print("-" * 70)

            for maven_path in found_paths:
                try:
                    print(f"Testing: {maven_path}")

                    # Try with shell=True
                    result = subprocess.run(
                        f'"{maven_path}" --version',
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=True
                    )

                    if result.returncode == 0:
                        print(f"✅ SUCCESS with shell=True")
                        print(f"   Version: {result.stdout.split(chr(10))[0]}")
                        print(f"\n{'=' * 70}")
                        print(f"RECOMMENDED MAVEN PATH:")
                        print(f"{maven_path}")
                        print(f"{'=' * 70}")
                        return maven_path
                    else:
                        print(f"❌ FAILED (return code: {result.returncode})")

                except Exception as e:
                    print(f"❌ ERROR: {e}")

    print("\n" + "=" * 70)
    print("❌ Maven NOT FOUND")
    print("=" * 70)
    print("\nPlease install Maven:")
    print("1. Download from: https://maven.apache.org/download.cgi")
    print("2. Extract to: C:\\Maven\\apache-maven-X.X.X")
    print("3. Add to PATH or set manually in the app")
    print("=" * 70)

    return None


if __name__ == "__main__":
    maven_cmd = test_maven_detection()

    if maven_cmd:
        print(f"\n✅ Maven is ready to use!")
        print(f"   Command: {maven_cmd}")

        # Test actual execution
        print("\n[Test 4] Test Maven execution")
        print("-" * 70)

        try:
            is_windows = sys.platform.startswith('win')

            if is_windows:
                cmd_str = f'"{maven_cmd}" --version'
                print(f"Command: {cmd_str}")
                result = subprocess.run(
                    cmd_str,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
            else:
                print(f"Command: {maven_cmd} --version")
                result = subprocess.run(
                    [maven_cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=False
                )

            print("\nOutput:")
            print(result.stdout)

            if result.returncode == 0:
                print("✅ Maven execution test PASSED!")
            else:
                print(f"❌ Maven execution test FAILED (return code: {result.returncode})")

        except Exception as e:
            print(f"❌ Maven execution test ERROR: {e}")
    else:
        sys.exit(1)