"""
Git repository management service - FIXED for Windows
Key fixes:
1. Proper subprocess shell=True for Windows
2. Better error handling for path issues
3. Uses raw strings for Windows paths
"""

import subprocess
import shutil
import sys
from pathlib import Path
from typing import Optional, List


class GitService:
    """Handles Git operations with optimized cloning and updating"""

    def __init__(self, git_cmd: str = "git", timeout: int = 600):
        self.git_cmd = git_cmd
        self.timeout = timeout
        self.log_callback = None
        self.is_windows = sys.platform.startswith('win')

    def set_log_callback(self, callback):
        """Set logging callback"""
        self.log_callback = callback

    def log(self, message: str):
        """Log message"""
        if self.log_callback:
            self.log_callback(message)

    def _run_git_command(self, args: List[str], cwd: str = None, timeout: int = None) -> subprocess.CompletedProcess:
        """
        Run git command with proper Windows handling
        """
        if timeout is None:
            timeout = self.timeout

        # Ensure cwd is a string
        if cwd and isinstance(cwd, Path):
            cwd = str(cwd)

        try:
            # On Windows, use shell=True for better path handling
            result = subprocess.run(
                args,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=self.is_windows  # Use shell on Windows
            )
            return result
        except FileNotFoundError as e:
            self.log(f"   ❌ Command not found: {e}")
            raise
        except Exception as e:
            self.log(f"   ❌ Command error: {e}")
            raise

    def get_current_branch(self, repo_path: Path) -> Optional[str]:
        """Get current branch name"""
        try:
            result = self._run_git_command(
                [self.git_cmd, "branch", "--show-current"],
                cwd=repo_path,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def get_commit_hash(self, repo_path: Path) -> Optional[str]:
        """Get current commit hash"""
        try:
            result = self._run_git_command(
                [self.git_cmd, "rev-parse", "HEAD"],
                cwd=repo_path,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def list_branches(self, repo_path: Path) -> List[str]:
        """List all available branches"""
        try:
            # Fetch to get latest branches
            self._run_git_command(
                [self.git_cmd, "fetch", "--all"],
                cwd=repo_path,
                timeout=30
            )

            result = self._run_git_command(
                [self.git_cmd, "branch", "-r"],
                cwd=repo_path,
                timeout=10
            )

            if result.returncode == 0:
                branches = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and 'HEAD' not in line:
                        # Remove 'origin/' prefix
                        branch = line.replace('origin/', '')
                        branches.append(branch)
                return sorted(set(branches))
        except:
            pass
        return []

    def clone_or_update_repo(self, repo_url: str, repo_path: Path, branch: str = "master") -> bool:
        """
        Clone repository or update if exists, switch to specified branch
        Fixed for Windows path handling
        """
        try:
            # Ensure repo_path is absolute
            repo_path = repo_path.resolve()

            if repo_path.exists():
                self.log(f"📂 Repository exists at {repo_path.name}")

                # Verify it's a git repo
                git_dir = repo_path / ".git"
                if not git_dir.exists():
                    self.log(f"   ⚠️ Not a git repository, removing and re-cloning...")
                    shutil.rmtree(repo_path, ignore_errors=True)
                    return self.clone_or_update_repo(repo_url, repo_path, branch)

                current_branch = self.get_current_branch(repo_path)
                self.log(f"   📍 Current branch: {current_branch}")
                self.log(f"   🎯 Target branch: {branch}")

                # Fetch latest changes
                self.log(f"   ⬇️ Fetching updates...")
                result = self._run_git_command(
                    [self.git_cmd, "fetch", "--all", "--prune"],
                    cwd=repo_path
                )

                if result.returncode != 0:
                    self.log(f"   ⚠️ Fetch warning: {result.stderr.strip()}")

                # Reset any local changes
                self._run_git_command(
                    [self.git_cmd, "reset", "--hard"],
                    cwd=repo_path,
                    timeout=30
                )

                # Switch to target branch if different
                if current_branch != branch:
                    self.log(f"   🔄 Switching from {current_branch} to {branch}")

                    # Try to checkout branch
                    result = self._run_git_command(
                        [self.git_cmd, "checkout", branch],
                        cwd=repo_path,
                        timeout=30
                    )

                    if result.returncode != 0:
                        # Branch might not exist locally, try to create from remote
                        self.log(f"   🆕 Creating local branch from origin/{branch}")
                        result = self._run_git_command(
                            [self.git_cmd, "checkout", "-b", branch, f"origin/{branch}"],
                            cwd=repo_path,
                            timeout=30
                        )

                        if result.returncode != 0:
                            self.log(f"   ❌ Failed to checkout branch: {result.stderr.strip()}")
                            return False

                    self.log(f"   ✅ Successfully switched to {branch}")

                # Pull latest changes
                self.log(f"   ⬇️ Pulling latest changes from {branch}...")
                result = self._run_git_command(
                    [self.git_cmd, "pull", "--rebase"],
                    cwd=repo_path
                )

                if result.returncode == 0:
                    commit_hash = self.get_commit_hash(repo_path)
                    self.log(f"   ✅ Updated successfully (commit: {commit_hash[:8] if commit_hash else 'unknown'})")
                else:
                    self.log(f"   ⚠️ Pull warning: {result.stderr.strip()}")

            else:
                # Clone repository with specified branch
                self.log(f"📥 Cloning {repo_url}")
                self.log(f"   📍 Branch: {branch}")
                self.log(f"   📂 Destination: {repo_path}")

                # Ensure parent directory exists
                repo_path.parent.mkdir(parents=True, exist_ok=True)

                # Clone with specific branch
                result = self._run_git_command(
                    [self.git_cmd, "clone", "--branch", branch, "--single-branch",
                     "--depth", "1", repo_url, str(repo_path)]
                )

                if result.returncode != 0:
                    # Try without branch specification (in case branch doesn't exist)
                    self.log(f"   ⚠️ Branch {branch} not found, trying default branch...")

                    # Remove failed clone directory
                    if repo_path.exists():
                        shutil.rmtree(repo_path, ignore_errors=True)

                    result = self._run_git_command(
                        [self.git_cmd, "clone", "--depth", "1", repo_url, str(repo_path)]
                    )

                    if result.returncode != 0:
                        self.log(f"   ❌ Clone failed: {result.stderr.strip()}")
                        return False

                    # After cloning with default branch, try to checkout the requested branch
                    self.log(f"   🔄 Attempting to checkout {branch}...")

                    # Fetch all branches first
                    self._run_git_command(
                        [self.git_cmd, "fetch", "--all"],
                        cwd=repo_path,
                        timeout=60
                    )

                    result = self._run_git_command(
                        [self.git_cmd, "checkout", "-b", branch, f"origin/{branch}"],
                        cwd=repo_path,
                        timeout=30
                    )

                    if result.returncode != 0:
                        self.log(f"   ⚠️ Could not checkout {branch}, staying on default branch")

                self.log(f"   ✅ Clone completed successfully")

            # Verify pom.xml exists
            pom_file = repo_path / "pom.xml"
            if pom_file.exists():
                self.log(f"   ✅ Found pom.xml")
            else:
                self.log(f"   ⚠️ Warning: pom.xml not found")

            return True

        except subprocess.TimeoutExpired:
            self.log(f"   ❌ Git operation timed out")
            return False
        except FileNotFoundError as e:
            self.log(f"   ❌ Path error: {str(e)}")
            self.log(f"   💡 Make sure Git is installed and in PATH")
            self.log(f"   💡 Repository path: {repo_path}")
            return False
        except Exception as e:
            self.log(f"   ❌ Error: {str(e)}")
            import traceback
            self.log(f"   Debug info: {traceback.format_exc()}")
            return False