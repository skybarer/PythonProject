"""
builder.py - FULLY FIXED FOR ALL BRANCHES
Now: dev, feature/*, release/1.0 → ALL WORK!
"""

import os
import subprocess
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict

from .git_service import GitService
from .build_cache import BuildCache
from ..utils.system_info import SystemInfo
from .command_finder import CommandFinder


@dataclass
class BuildConfig:
    """Configuration for a microservice build"""
    service_name: str
    group_id: str
    repo_url: str
    branch: str
    settings_file: str
    maven_profiles: List[str]
    jvm_options: str
    maven_threads: int = 4
    force_full_fetch: bool = False   # NEW: Force unshallow for non-default branches


class MicroserviceBuilder:
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)

        self.sys_info = SystemInfo()
        self.max_workers = self.sys_info.recommended_workers

        self.build_cache = BuildCache()
        self.command_finder = CommandFinder()
        self.git_service = None

        self.maven_cmd = None
        self.git_cmd = None
        self._find_commands()

        self.log_callbacks = []
        self.log_lock = threading.Lock()

    def _find_commands(self):
        self.maven_cmd = self.command_finder.find_maven()
        self.git_cmd = self.command_finder.find_git()
        if self.git_cmd:
            self.git_service = GitService(self.git_cmd)
            self.git_service.set_log_callback(self.log)

    def add_log_callback(self, callback):
        self.log_callbacks.append(callback)

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        with self.log_lock:
            print(log_message)
            for cb in self.log_callbacks:
                try: cb(log_message)
                except: pass

    def check_prerequisites(self) -> Dict:
        results = {}
        if self.git_cmd:
            info = self.command_finder.verify_git(self.git_cmd)
            results['git'] = info
            self.log(f"Git: {info['version']}" if info['available'] else "Git: Not found")
        else:
            results['git'] = {'available': False}

        if self.maven_cmd:
            info = self.command_finder.verify_maven(self.maven_cmd)
            results['maven'] = info
            self.log(f"Maven: {info['version']}" if info['available'] else "Maven: Not found")
        else:
            results['maven'] = {'available': False}

        return results

    def get_optimized_maven_opts(self, config: BuildConfig) -> str:
        return config.jvm_options or self.sys_info.get_optimized_maven_opts()

    def build_service(self, config: BuildConfig, force: bool = False) -> Dict:
        start_time = time.time()
        result = {
            "service": config.service_name,
            "status": "pending",
            "duration": 0,
            "error": None,
            "branch": config.branch
        }

        try:
            self.log(f"\nBUILDING: {config.service_name} → {config.branch}")

            repo_dir = self.workspace_dir / config.group_id / config.service_name
            repo_dir.mkdir(parents=True, exist_ok=True)

            if not self.git_service:
                raise Exception("Git not available")

            # 1. Clone or update
            success = self.git_service.clone_or_update_repo(
                config.repo_url,
                repo_dir,
                config.branch
            )

            if not success:
                raise Exception("Git clone/update failed")

            # 2. FORCE FULL FETCH IF NON-DEFAULT BRANCH
            if config.force_full_fetch:
                self.log(f"Non-default branch detected → unshallowing")
                self.git_service._run_git_command(
                    [self.git_cmd, "fetch", "--unshallow", "--all", "--tags"],
                    cwd=repo_dir,
                    timeout=180
                )
                self.git_service._run_git_command(
                    [self.git_cmd, "remote", "set-branches", "origin", "*"],
                    cwd=repo_dir
                )

            # 3. HARD CHECKOUT (fails loudly if branch missing)
            checkout = self.git_service._run_git_command(
                [self.git_cmd, "checkout", config.branch],
                cwd=repo_dir,
                timeout=30
            )
            if checkout.returncode != 0:
                self.log(f"Checkout failed → trying from origin")
                create = self.git_service._run_git_command(
                    [self.git_cmd, "checkout", "-b", config.branch, f"origin/{config.branch}"],
                    cwd=repo_dir,
                    timeout=30
                )
                if create.returncode != 0:
                    raise Exception(f"Cannot checkout branch: {config.branch}")

            current = self.git_service.get_current_branch(repo_dir)
            commit = self.git_service.get_commit_hash(repo_dir)[:8]
            self.log(f"Checked out: {current} ({commit})")

            # 4. Skip if no changes
            if not force and not self.build_cache.should_build(config.service_name, str(repo_dir)):
                result["status"] = "skipped"
                result["duration"] = time.time() - start_time
                self.log(f"SKIPPED (cached)")
                return result

            # 5. Verify pom.xml
            if not (repo_dir / "pom.xml").exists():
                raise Exception("pom.xml not found")

            # 6. Build command
            cmd = [
                self.maven_cmd, "clean", "install",
                "-DskipTests", "-T", str(config.maven_threads),
                f"-Dmaven.repo.local={self.workspace_dir}/.m2/repository",
                "-Drat.skip=true", "-Dmaven.javadoc.skip=true",
                "-Dcheckstyle.skip=true", "-Denforcer.skip=true"
            ]

            if config.settings_file and Path(config.settings_file).exists():
                cmd.extend(["-s", config.settings_file])

            if config.maven_profiles:
                cmd.append(f"-P{','.join(config.maven_profiles)}")

            env = os.environ.copy()
            env["MAVEN_OPTS"] = self.get_optimized_maven_opts(config)

            self.log(f"Running Maven...")
            proc = subprocess.run(
                cmd,
                cwd=str(repo_dir),
                capture_output=True,
                text=True,
                env=env,
                timeout=1800
            )

            if proc.returncode == 0:
                result["status"] = "success"
                self.build_cache.mark_built(config.service_name, str(repo_dir), config.branch)
                self.log(f"SUCCESS in {time.time()-start_time:.1f}s")
            else:
                result["status"] = "failed"
                result["error"] = proc.stderr[-800:]
                self.log(f"FAILED")
                for line in proc.stderr.strip().split('\n')[-10:]:
                    self.log(f"   {line}")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.log(f"ERROR: {e}")

        result["duration"] = time.time() - start_time
        return result

    def build_services(self, configs: List[BuildConfig], force: bool = False) -> List[Dict]:
        self.log(f"\nSTARTING BUILD: {len(configs)} services | Workers: {self.max_workers}")
        prereqs = self.check_prerequisites()
        if not prereqs['git']['available'] or not prereqs['maven']['available']:
            return [{"status": "error", "error": "Git/Maven missing"} for _ in configs]

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self.build_service, c, force): c for c in configs}
            for f in as_completed(futures):
                results.append(f.result())

        success = sum(1 for r in results if r['status'] == 'success')
        self.log(f"\nBUILD COMPLETE: {success}/{len(results)} succeeded")
        return results