"""
High-performance microservice builder with maximum optimization
"""

import os
import subprocess
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
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


class MicroserviceBuilder:
    """High-performance microservice builder"""

    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)

        # System information
        self.sys_info = SystemInfo()
        self.max_workers = self.sys_info.recommended_workers

        # Services
        self.build_cache = BuildCache()
        self.command_finder = CommandFinder()
        self.git_service = None

        # Commands
        self.maven_cmd = None
        self.git_cmd = None
        self._find_commands()

        # Logging
        self.log_callbacks = []
        self.log_lock = threading.Lock()

    def _find_commands(self):
        """Find Maven and Git commands"""
        self.maven_cmd = self.command_finder.find_maven()
        self.git_cmd = self.command_finder.find_git()

        if self.git_cmd:
            self.git_service = GitService(self.git_cmd)
            self.git_service.set_log_callback(self.log)

    def add_log_callback(self, callback):
        """Add callback for logging"""
        self.log_callbacks.append(callback)

    def log(self, message: str):
        """Thread-safe logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        with self.log_lock:
            print(log_message)
            for callback in self.log_callbacks:
                try:
                    callback(log_message)
                except:
                    pass

    def check_prerequisites(self) -> Dict[str, dict]:
        """Check if Git and Maven are available"""
        results = {}

        # Git check
        if self.git_cmd:
            git_info = self.command_finder.verify_git(self.git_cmd)
            results['git'] = git_info
            if git_info['available']:
                self.log(f"✅ Git: {git_info['version']}")
            else:
                self.log(f"❌ Git: Not available")
        else:
            results['git'] = {'available': False, 'version': 'Not found', 'path': None}
            self.log("❌ Git: Not found in PATH")

        # Maven check
        if self.maven_cmd:
            maven_info = self.command_finder.verify_maven(self.maven_cmd)
            results['maven'] = maven_info
            if maven_info['available']:
                self.log(f"✅ Maven: {maven_info['version']}")
            else:
                self.log(f"❌ Maven: Not available")
        else:
            results['maven'] = {'available': False, 'version': 'Not found', 'path': None}
            self.log("❌ Maven: Not found in PATH")

        return results

    def get_optimized_maven_opts(self, config: BuildConfig) -> str:
        """Get optimized Maven JVM options"""
        if config.jvm_options:
            return config.jvm_options
        return self.sys_info.get_optimized_maven_opts()

    def build_service(self, config: BuildConfig, force: bool = False) -> Dict:
        """Build a single microservice with maximum optimization"""
        start_time = time.time()
        result = {
            "service": config.service_name,
            "status": "pending",
            "duration": 0,
            "error": None,
            "branch": config.branch
        }

        try:
            self.log(f"\n{'=' * 80}")
            self.log(f"🚀 Building: {config.service_name} (branch: {config.branch})")
            self.log(f"{'=' * 80}")

            # Clone or update repository
            repo_dir = self.workspace_dir / config.group_id / config.service_name

            if not self.git_service:
                raise Exception("Git service not initialized")

            success = self.git_service.clone_or_update_repo(
                config.repo_url,
                repo_dir,
                config.branch
            )

            if not success:
                raise Exception("Failed to clone/update repository")

            # Check if build is needed
            if not force and not self.build_cache.should_build(config.service_name, str(repo_dir)):
                result["status"] = "skipped"
                result["duration"] = time.time() - start_time
                self.log(f"⭐️ {config.service_name} - SKIPPED (no changes)")
                return result

            # Verify pom.xml
            pom_file = repo_dir / "pom.xml"
            if not pom_file.exists():
                raise Exception(f"pom.xml not found in {repo_dir}")

            # Build Maven command with optimizations
            maven_cmd = [
                self.maven_cmd,
                "clean", "install",
                "-DskipTests",
                "-T", str(config.maven_threads),  # Multi-threaded build
                f"-Dmaven.repo.local={self.workspace_dir}/.m2/repository",
                "-Drat.skip=true",  # Skip RAT checks
                "-Dmaven.javadoc.skip=true",  # Skip JavaDoc
                "-Dcheckstyle.skip=true",  # Skip checkstyle
                "-Denforcer.skip=true"  # Skip enforcer
            ]

            # Add settings file
            if config.settings_file and Path(config.settings_file).exists():
                maven_cmd.extend(["-s", config.settings_file])
                self.log(f"📄 Settings: {Path(config.settings_file).name}")

            # Add profiles
            if config.maven_profiles:
                profiles = ','.join(config.maven_profiles)
                maven_cmd.append(f"-P{profiles}")
                self.log(f"📋 Profiles: {profiles}")

            # Optimized JVM options
            jvm_opts = self.get_optimized_maven_opts(config)
            env = os.environ.copy()
            env["MAVEN_OPTS"] = jvm_opts

            self.log(f"⚙️ JVM: {jvm_opts}")
            self.log(f"🧵 Threads: {config.maven_threads}")
            self.log(f"🔨 Building...")

            # Execute build
            process = subprocess.run(
                maven_cmd,
                cwd=str(repo_dir),
                capture_output=True,
                text=True,
                env=env,
                timeout=1800
            )

            if process.returncode == 0:
                result["status"] = "success"
                self.build_cache.mark_built(config.service_name, str(repo_dir), config.branch)
                self.log(f"✅ {config.service_name} - BUILD SUCCESS")

                # Show build summary
                if process.stdout:
                    for line in process.stdout.strip().split('\n'):
                        if 'BUILD SUCCESS' in line or 'Total time' in line:
                            self.log(f"   {line.strip()}")
            else:
                result["status"] = "failed"
                result["error"] = process.stderr[-1000:] if process.stderr else "Unknown error"
                self.log(f"❌ {config.service_name} - BUILD FAILED")

                # Log errors
                if process.stderr:
                    error_lines = process.stderr.strip().split('\n')
                    self.log("💥 Error output (last 20 lines):")
                    for line in error_lines[-20:]:
                        if line.strip():
                            self.log(f"   {line}")

                if process.stdout:
                    output_lines = process.stdout.strip().split('\n')
                    self.log("📜 Build output (last 15 lines):")
                    for line in output_lines[-15:]:
                        if line.strip():
                            self.log(f"   {line}")

        except subprocess.TimeoutExpired:
            result["status"] = "error"
            result["error"] = "Build timeout (30 minutes)"
            self.log(f"⏱️ {config.service_name} - TIMEOUT")
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.log(f"❌ {config.service_name} - ERROR: {str(e)}")

        result["duration"] = time.time() - start_time
        self.log(f"⏱️ Duration: {result['duration']:.2f}s")

        return result

    def build_services(self, configs: List[BuildConfig], force: bool = False) -> List[Dict]:
        """Build multiple services with maximum parallelization"""
        self.log(f"\n{'=' * 80}")
        self.log(f"🏗️ Parallel Build Session")
        self.log(f"{'=' * 80}")
        self.log(f"📦 Services: {len(configs)}")
        self.log(f"⚡ Workers: {self.max_workers}")
        self.log(f"💻 CPU Cores: {self.sys_info.cpu_logical_count}")
        self.log(f"💾 Available RAM: {self.sys_info.available_memory_gb:.1f} GB")
        self.log(f"🔄 Force rebuild: {force}")
        self.log(f"{'=' * 80}\n")

        # Check prerequisites
        prereqs = self.check_prerequisites()
        if not prereqs.get('git', {}).get('available') or not prereqs.get('maven', {}).get('available'):
            self.log("❌ FATAL: Prerequisites not met")
            return [{
                "service": config.service_name,
                "status": "error",
                "error": "Prerequisites not met",
                "duration": 0,
                "branch": config.branch
            } for config in configs]

        results = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.build_service, config, force): config
                for config in configs
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        total_duration = time.time() - start_time

        # Summary
        self.log(f"\n{'=' * 80}")
        self.log(f"📊 BUILD SUMMARY")
        self.log(f"{'=' * 80}")

        success = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'failed')
        skipped = sum(1 for r in results if r['status'] == 'skipped')
        errors = sum(1 for r in results if r['status'] == 'error')

        self.log(f"✅ Success: {success}")
        self.log(f"❌ Failed: {failed}")
        self.log(f"⭐️ Skipped: {skipped}")
        self.log(f"💥 Errors: {errors}")
        self.log(f"⏱️ Total time: {total_duration:.2f}s")

        if success > 0:
            avg_time = sum(r['duration'] for r in results if r['status'] == 'success') / success
            self.log(f"📈 Avg build time: {avg_time:.2f}s")

        self.log(f"{'=' * 80}\n")

        return results