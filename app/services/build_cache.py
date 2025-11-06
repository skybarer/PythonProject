"""
Build cache management
"""

import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class BuildCache:
    """Manages build cache to skip unchanged builds"""

    def __init__(self, cache_dir: str = ".build_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load cache from file"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def get_commit_hash(self, repo_path: str) -> Optional[str]:
        """Get current commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None

    def get_pom_hash(self, repo_path: str) -> Optional[str]:
        """Get hash of pom.xml"""
        pom_file = Path(repo_path) / "pom.xml"
        if pom_file.exists():
            with open(pom_file, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        return None

    def should_build(self, service_name: str, repo_path: str) -> bool:
        """Check if service needs to be built"""
        commit_hash = self.get_commit_hash(repo_path)
        pom_hash = self.get_pom_hash(repo_path)

        if not commit_hash or not pom_hash:
            return True

        cache_key = service_name
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if (cached.get("commit") == commit_hash and
                    cached.get("pom") == pom_hash):
                return False

        return True

    def mark_built(self, service_name: str, repo_path: str, branch: str = ""):
        """Mark service as built"""
        commit_hash = self.get_commit_hash(repo_path)
        pom_hash = self.get_pom_hash(repo_path)

        self.cache[service_name] = {
            "commit": commit_hash,
            "pom": pom_hash,
            "branch": branch,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache()

    def get_cache_info(self, service_name: str) -> Optional[Dict]:
        """Get cache information for a service"""
        return self.cache.get(service_name)

    def clear(self):
        """Clear all cache"""
        self.cache = {}
        self._save_cache()

    def clear_service(self, service_name: str):
        """Clear cache for specific service"""
        if service_name in self.cache:
            del self.cache[service_name]
            self._save_cache()