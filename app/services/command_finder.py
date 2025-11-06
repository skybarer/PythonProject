"""
Find and verify system commands (Git, Maven)
"""

import subprocess
from pathlib import Path
from typing import Optional, Dict


class CommandFinder:
    """Find and verify system commands"""

    def find_git(self) -> Optional[str]:
        """Find Git command"""
        git_locations = ["git", "git.exe"]

        for git_cmd in git_locations:
            if self._verify_command(git_cmd):
                return git_cmd

        return None

    def find_maven(self) -> Optional[str]:
        """Find Maven command"""
        maven_locations = [
            "mvn",
            "mvn.cmd",
        ]

        # Check common Windows locations
        user_home = Path.home()
        common_paths = [
            user_home / "Documents" / "software",
            Path("C:/Program Files/Apache/Maven"),
            Path("C:/Program Files/Maven"),
            Path("C:/Maven"),
            user_home / "apache-maven",
        ]

        # Search common locations
        for base_path in common_paths:
            if base_path.exists():
                for item in base_path.iterdir():
                    if item.is_dir() and 'maven' in item.name.lower():
                        maven_bin = item / "bin" / "mvn.cmd"
                        if maven_bin.exists():
                            maven_locations.append(str(maven_bin))

        # Test Maven commands
        for maven_cmd in maven_locations:
            if self._verify_command(maven_cmd):
                return maven_cmd

        return None

    def _verify_command(self, cmd: str) -> bool:
        """Verify if command works"""
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            return result.returncode == 0
        except:
            return False

    def verify_git(self, git_cmd: str) -> Dict:
        """Verify Git installation"""
        try:
            result = subprocess.run(
                [git_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )

            if result.returncode == 0:
                return {
                    'available': True,
                    'version': result.stdout.strip(),
                    'path': git_cmd
                }
        except Exception as e:
            return {
                'available': False,
                'version': str(e),
                'path': None
            }

        return {
            'available': False,
            'version': 'Not found',
            'path': None
        }

    def verify_maven(self, maven_cmd: str) -> Dict:
        """Verify Maven installation"""
        try:
            result = subprocess.run(
                [maven_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )

            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return {
                    'available': True,
                    'version': version_line,
                    'path': maven_cmd
                }
        except Exception as e:
            return {
                'available': False,
                'version': str(e),
                'path': None
            }

        return {
            'available': False,
            'version': 'Not found',
            'path': None
        }