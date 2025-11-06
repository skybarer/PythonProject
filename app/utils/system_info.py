"""
System information utilities for optimal resource allocation
"""

import os
import platform
import psutil


class SystemInfo:
    """Provides system information for optimal build configuration"""

    def __init__(self):
        self.cpu_count = psutil.cpu_count(logical=False) or 1
        self.cpu_logical_count = psutil.cpu_count(logical=True) or 1
        self.total_memory = psutil.virtual_memory().total
        self.total_memory_gb = self.total_memory / (1024 ** 3)
        self.available_memory = psutil.virtual_memory().available
        self.available_memory_gb = self.available_memory / (1024 ** 3)
        self.os_name = platform.system()
        self.os_version = platform.version()

    @property
    def recommended_workers(self):
        """Calculate recommended number of parallel workers"""
        # Use 75% of CPU cores, minimum 2, maximum 16
        workers = max(2, min(16, int(self.cpu_logical_count * 0.75)))

        # Adjust based on available memory (assume 2GB per worker minimum)
        memory_based = int(self.available_memory_gb / 2)
        return min(workers, memory_based)

    @property
    def recommended_maven_threads(self):
        """Recommended threads for Maven builds"""
        # Use half of physical cores for Maven threading
        return max(2, int(self.cpu_count / 2))

    @property
    def recommended_jvm_memory(self):
        """Recommended JVM heap size in GB"""
        # Use 25% of available memory per build, minimum 2GB, maximum 8GB
        memory_per_build = self.available_memory_gb * 0.25
        return max(2, min(8, int(memory_per_build)))

    def get_optimized_maven_opts(self):
        """Get optimized Maven JVM options"""
        memory = self.recommended_jvm_memory
        threads = self.recommended_maven_threads

        return (f'-Xmx{memory}G -Xms{memory // 2}G '
                f'-XX:+UseParallelGC -XX:ParallelGCThreads={threads} '
                f'-XX:+TieredCompilation -XX:TieredStopAtLevel=1 '
                f'-Dmaven.artifact.threads={threads} '
                f'-Dmaven.compiler.fork=true '
                f'-Dmaven.compiler.maxmem={memory}g')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'cpu_cores': self.cpu_count,
            'cpu_logical_cores': self.cpu_logical_count,
            'total_memory_gb': round(self.total_memory_gb, 2),
            'available_memory_gb': round(self.available_memory_gb, 2),
            'recommended_workers': self.recommended_workers,
            'recommended_maven_threads': self.recommended_maven_threads,
            'recommended_jvm_memory': self.recommended_jvm_memory,
            'optimized_maven_opts': self.get_optimized_maven_opts(),
            'os_name': self.os_name,
            'os_version': self.os_version
        }