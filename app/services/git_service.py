"""
Git repository management service
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, List


class GitService:
    """Handles Git operations with optimized cloning and updating"""

    def __init__(self, git_cmd: str = "git", timeout: int = 600):
        self.git_cmd = git_cmd
        self.timeout = timeout
        self.log_callback = None

    def set_log_callback(self, callback):
        """Set logging callback"""
        self.log_callback = callback

    def log(self, message: str):
        """Log message"""
        if self.log_callback:
            self.log_callback(message)

    def get_current_branch(self, repo_path: Path) -> Optional[str]:
        """Get current branch name"""
        try:
            result = subprocess.run(
                [self.git_cmd, "branch", "--show-current"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
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
            result = subprocess.run(
                [self.git_cmd, "rev-parse", "HEAD"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
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
            subprocess.run(
                [self.git_cmd, "fetch", "--all"],
                cwd=str(repo_path),
                capture_output=True,
                timeout=30
            )

            result = subprocess.run(
                [self.git_cmd, "branch", "-r"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                branches = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and not 'HEAD' in line:
                        # Remove 'origin/' prefix
                        branch = line.replace('origin/', '')
                        branches.append(branch)
                return sorted(set(branches))
        except:
            pass
        return []

    def clone_or_update_repo(self, repo_url: str, repo_path: Path, branch: str = "master") -> bool:
        """Clone repository or update if exists, switch to specified branch"""
        try:
            if repo_path.exists():
                self.log(f"📂 Repository exists at {repo_path.name}")

                # Verify it's a git repo
                git_dir = repo_path / ".git"
                if not git_dir.exists():
                    self.log(f"   ⚠️ Not a git repository, removing and re-cloning...")
                    shutil.rmtree(repo_path)
                    return self.clone_or_update_repo(repo_url, repo_path, branch)

                current_branch = self.get_current_branch(repo_path)
                self.log(f"   🔍 Current branch: {current_branch}")

                # Fetch latest changes
                self.log(f"   ⬇️ Fetching updates...")
                result = subprocess.run(
                    [self.git_cmd, "fetch", "--all", "--prune"],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )

                if result.returncode != 0:
                    self.log(f"   ⚠️ Fetch warning: {result.stderr.strip()}")

                # Switch to target branch if different
                if current_branch != branch:
                    self.log(f"   🔄 Switching to branch: {branch}")

                    # Try to checkout branch
                    result = subprocess.run(
                        [self.git_cmd, "checkout", branch],
                        cwd=str(repo_path),
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.returncode != 0:
                        # Branch might not exist locally, try to create from remote
                        self.log(f"   🆕 Creating local branch from origin/{branch}")
                        result = subprocess.run(
                            [self.git_cmd, "checkout", "-b", branch, f"origin/{branch}"],
                            cwd=str(repo_path),
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        if result.returncode != 0:
                            self.log(f"   ❌ Failed to checkout branch: {result.stderr.strip()}")
                            return False

                # Pull latest changes
                self.log(f"   ⬇️ Pulling latest changes...")
                result = subprocess.run(
                    [self.git_cmd, "pull", "--rebase"],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )

                if result.returncode == 0:
                    commit_hash = self.get_commit_hash(repo_path)
                    self.log(f"   ✅ Updated successfully (commit: {commit_hash[:8] if commit_hash else 'unknown'})")
                else:
                    self.log(f"   ⚠️ Pull warning: {result.stderr.strip()}")

            else:
                # Clone repository
                self.log(f"📥 Cloning {repo_url}")
                self.log(f"   🔍 Branch: {branch}")
                self.log(f"   📂 Destination: {repo_path}")

                repo_path.parent.mkdir(parents=True, exist_ok=True)

                result = subprocess.run(
                    [self.git_cmd, "clone", "--branch", branch, "--single-branch",
                     "--depth", "1", repo_url, str(repo_path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )

                if result.returncode != 0:
                    # Try without branch specification (in case branch doesn't exist)
                    self.log(f"   ⚠️ Branch {branch} not found, cloning default branch...")
                    result = subprocess.run(
                        [self.git_cmd, "clone", "--depth", "1", repo_url, str(repo_path)],
                        capture_output=True,
                        text=True,
                        timeout=self.timeout
                    )

                    if result.returncode != 0:
                        self.log(f"   ❌ Clone failed: {result.stderr.strip()}")
                        return False

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
        except Exception as e:
            self.log(f"   ❌ Error: {str(e)}")
            return False