"""
builder.py - ULTRA-OPTIMIZED FOR MAXIMUM SPEED
Aggressive multi-threading, parallel builds, and resource maximization
FIXED: Windows Maven execution (WinError 2)
"""

import os
import subprocess
import time
import threading
import sys
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
    maven_threads: int = 8
    force_full_fetch: bool = False
    # Aggressive optimization flags
    skip_tests: bool = True
    skip_javadoc: bool = True
    skip_source: bool = True
    offline_mode: bool = False
    aggressive_parallel: bool = True


class MicroserviceBuilder:
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)

        self.sys_info = SystemInfo()
        self.max_workers = max(4, self.sys_info.cpu_logical_count)
        self.is_windows = sys.platform.startswith('win')

        self.build_cache = BuildCache()
        self.command_finder = CommandFinder()
        self.git_service = None

        self.maven_cmd = None
        self.git_cmd = None
        self._find_commands()

        self.log_callbacks = []
        self.log_lock = threading.Lock()
        self.build_start_time = None

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

    def get_ultra_optimized_maven_opts(self, config: BuildConfig) -> str:
        """ULTRA-AGGRESSIVE JVM settings for maximum build speed"""
        if config.jvm_options and config.jvm_options.strip():
            return config.jvm_options

        available_gb = self.sys_info.available_memory_gb
        heap_size = max(4, min(16, int(available_gb * 0.7)))
        gc_threads = self.sys_info.cpu_logical_count

        opts = [
            f'-Xmx{heap_size}G',
            f'-Xms{heap_size}G',
            '-XX:+UseParallelGC',
            f'-XX:ParallelGCThreads={gc_threads}',
            '-XX:+AggressiveOpts',
            '-XX:+UseFastAccessorMethods',
            '-XX:+OptimizeStringConcat',
            '-XX:+UseCompressedOops',
            '-XX:ReservedCodeCacheSize=512M',
            '-XX:+TieredCompilation',
            '-XX:TieredStopAtLevel=1',
            '-XX:CICompilerCount=4',
            '-Djava.awt.headless=true',
            f'-Dmaven.artifact.threads={gc_threads}',
            '-Dmaven.compiler.fork=true',
            f'-Dmaven.compiler.maxmem={heap_size}g',
            '-Daether.connector.http.connectionMaxTtl=30',
            '-Daether.connector.requestTimeout=30000',
        ]

        return ' '.join(opts)

    def _run_maven_command(self, cmd: List[str], cwd: str, env: dict, timeout: int = 1800) -> subprocess.CompletedProcess:
        """
        Run Maven command with proper Windows handling
        CRITICAL FIX: Use shell=False with list args (Method 3) - this works!
        """
        self.log(f"Executing Maven in: {cwd}")

        if self.is_windows:
            # WINDOWS: Use shell=False with list args (Method 3 - confirmed working!)
            # Do NOT use cmd.exe /c or shell=True - these fail with mvn.cmd

            self.log(f"Command (Windows): {' '.join(str(x) for x in cmd)[:150]}...")

            result = subprocess.run(
                cmd,  # Use list directly
                cwd=cwd,
                capture_output=True,
                text=True,
                env=env,
                timeout=timeout,
                shell=False,  # Critical: shell=False works for mvn.cmd!
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            # UNIX: Same method
            self.log(f"Command (Unix): {' '.join(cmd)[:200]}...")

            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                env=env,
                timeout=timeout,
                shell=False
            )

        return result

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
            self.log(f"\n{'='*60}")
            self.log(f"BUILDING: {config.service_name} → {config.branch}")
            self.log(f"{'='*60}")

            repo_dir = self.workspace_dir / config.group_id / config.service_name
            repo_dir.mkdir(parents=True, exist_ok=True)

            if not self.git_service:
                raise Exception("Git not available")

            # 1. Clone or update
            clone_start = time.time()
            success = self.git_service.clone_or_update_repo(
                config.repo_url,
                repo_dir,
                config.branch
            )
            clone_time = time.time() - clone_start
            self.log(f"Git operations: {clone_time:.1f}s")

            if not success:
                raise Exception("Git clone/update failed")

            # 2. Force full fetch if needed
            if config.force_full_fetch:
                self.log(f"Non-default branch → unshallowing")
                self.git_service._run_git_command(
                    [self.git_cmd, "fetch", "--unshallow", "--all", "--tags"],
                    cwd=repo_dir,
                    timeout=180
                )

            # 3. Checkout
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
            self.log(f"✓ Checked out: {current} ({commit})")

            # 4. Skip if cached
            if not force and not self.build_cache.should_build(config.service_name, str(repo_dir)):
                result["status"] = "skipped"
                result["duration"] = time.time() - start_time
                self.log(f"⚡ SKIPPED (cached) - {result['duration']:.1f}s")
                return result

            # 5. Verify pom.xml
            if not (repo_dir / "pom.xml").exists():
                raise Exception("pom.xml not found")

            # 6. BUILD COMMAND - ULTRA OPTIMIZED
            self.log(f"🚀 Starting ULTRA-FAST Maven build...")

            maven_threads = max(config.maven_threads, self.sys_info.cpu_logical_count)

            cmd = [
                self.maven_cmd,
                "clean", "install",
                f"-T",
                f"{maven_threads}C",  # Separate argument for better parsing
            ]

            # AGGRESSIVE SKIP FLAGS
            if config.skip_tests:
                cmd.extend(["-DskipTests", "-Dmaven.test.skip=true"])

            cmd.extend([
                "-Drat.skip=true",
                "-Denforcer.skip=true",
                "-Dcheckstyle.skip=true",
                "-Dpmd.skip=true",
                "-Dcpd.skip=true",
                "-Dspotbugs.skip=true",
                "-Dfindbugs.skip=true",
            ])

            if config.skip_javadoc:
                cmd.extend([
                    "-Dmaven.javadoc.skip=true",
                    "-Djavadoc.skip=true",
                ])

            if config.skip_source:
                cmd.append("-Dmaven.source.skip=true")

            # Custom local repository
            cmd.append(f"-Dmaven.repo.local={self.workspace_dir}/.m2/repository")

            # Offline mode
            if config.offline_mode:
                cmd.append("-o")
                self.log("📴 OFFLINE MODE - Using local cache only")

            # Settings file
            if config.settings_file and Path(config.settings_file).exists():
                cmd.extend(["-s", config.settings_file])

            # Profiles
            if config.maven_profiles:
                cmd.append(f"-P{','.join(config.maven_profiles)}")

            # PERFORMANCE FLAGS
            cmd.extend([
                "-B",  # Batch mode
                "-q",  # Quiet mode
                "-Dstyle.color=never",
                "-Dmaven.artifact.threads=16",
                "-Daether.connector.basic.threads=16",
            ])

            # Environment with ULTRA-OPTIMIZED JVM options
            env = os.environ.copy()
            env["MAVEN_OPTS"] = self.get_ultra_optimized_maven_opts(config)
            env["MAVEN_OPTS"] += " -Dmaven.wagon.http.pool=true"
            env["MAVEN_OPTS"] += " -Dmaven.wagon.http.retryHandler.count=2"

            self.log(f"JVM Heap: {env['MAVEN_OPTS'][:80]}...")
            self.log(f"Using {maven_threads} CPU cores for parallel build")

            # RUN MAVEN with proper Windows handling
            build_start = time.time()
            proc = self._run_maven_command(cmd, str(repo_dir), env, timeout=1800)
            build_time = time.time() - build_start

            if proc.returncode == 0:
                result["status"] = "success"
                self.build_cache.mark_built(config.service_name, str(repo_dir), config.branch)
                total_time = time.time() - start_time
                self.log(f"✅ SUCCESS - Build: {build_time:.1f}s, Total: {total_time:.1f}s")
                self.log(f"   Speed: {(build_time/60):.1f} minutes")
            else:
                result["status"] = "failed"
                result["error"] = proc.stderr[-1000:] if proc.stderr else "Build failed"
                self.log(f"❌ FAILED - {time.time()-start_time:.1f}s")

                if proc.stderr:
                    error_lines = proc.stderr.strip().split('\n')
                    self.log("Last 15 error lines:")
                    for line in error_lines[-15:]:
                        self.log(f"   {line}")

        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = "Build timeout (30 minutes exceeded)"
            self.log(f"⏱️ TIMEOUT after 30 minutes")
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.log(f"❌ ERROR: {e}")
            import traceback
            self.log(traceback.format_exc())

        result["duration"] = time.time() - start_time
        return result

    def build_services(self, configs: List[BuildConfig], force: bool = False) -> List[Dict]:
        """Build multiple services in parallel with MAXIMUM resource utilization"""
        self.build_start_time = time.time()

        self.log(f"\n{'='*70}")
        self.log(f"🚀 ULTRA-FAST PARALLEL BUILD")
        self.log(f"{'='*70}")
        self.log(f"Services: {len(configs)}")
        self.log(f"Parallel Workers: {self.max_workers}")
        self.log(f"CPU Cores: {self.sys_info.cpu_logical_count} (using ALL)")
        self.log(f"Available RAM: {self.sys_info.available_memory_gb:.1f} GB")
        self.log(f"Platform: {'Windows' if self.is_windows else 'Unix'}")
        self.log(f"Maven: {self.maven_cmd}")
        self.log(f"{'='*70}\n")

        prereqs = self.check_prerequisites()
        if not prereqs['git']['available'] or not prereqs['maven']['available']:
            return [{"status": "error", "error": "Git/Maven missing"} for _ in configs]

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self.build_service, c, force): c for c in configs}

            completed = 0
            total = len(configs)

            for f in as_completed(futures):
                result = f.result()
                results.append(result)
                completed += 1

                elapsed = time.time() - self.build_start_time
                avg_time = elapsed / completed
                eta = avg_time * (total - completed)

                self.log(f"\n{'='*70}")
                self.log(f"Progress: {completed}/{total} ({(completed/total*100):.1f}%)")
                self.log(f"Elapsed: {elapsed/60:.1f} min | ETA: {eta/60:.1f} min")
                self.log(f"{'='*70}\n")

        total_time = time.time() - self.build_start_time
        success = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'failed')
        skipped = sum(1 for r in results if r['status'] == 'skipped')

        self.log(f"\n{'='*70}")
        self.log(f"BUILD COMPLETE - {total_time/60:.1f} minutes")
        self.log(f"{'='*70}")
        self.log(f"✅ Success: {success}")
        self.log(f"❌ Failed: {failed}")
        self.log(f"⚡ Skipped: {skipped}")
        self.log(f"⏱️  Total Time: {total_time/60:.1f} minutes")
        self.log(f"⚡ Average per service: {total_time/len(configs):.1f} seconds")
        self.log(f"{'='*70}\n")

        return results