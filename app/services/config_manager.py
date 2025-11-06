"""
Configuration management service
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class ConfigManager:
    """Manages configuration files and settings"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.settings_dir = self.config_dir / "settings"
        self.settings_dir.mkdir(exist_ok=True)

    def load_gitlab_config(self) -> Dict:
        """Load GitLab configuration"""
        config_file = self.config_dir / "gitlab_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {
            "gitlab_url": "https://gitlab.com",
            "private_token": "",
            "maven_path": "",
            "git_path": ""
        }

    def save_gitlab_config(self, config: Dict):
        """Save GitLab configuration"""
        config_file = self.config_dir / "gitlab_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def load_group_settings(self, group_id: str) -> Dict:
        """Load settings for a specific group"""
        settings_file = self.settings_dir / f"{group_id}_settings.json"
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {
            "settings_xml_path": "",
            "default_profiles": [],
            "jvm_options": "",
            "maven_threads": 4
        }

    def save_group_settings(self, group_id: str, settings: Dict):
        """Save settings for a specific group"""
        settings_file = self.settings_dir / f"{group_id}_settings.json"
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def save_settings_xml(self, group_id: str, content: str) -> str:
        """Save Maven settings.xml content"""
        settings_file = self.settings_dir / f"{group_id}_settings.xml"
        with open(settings_file, 'w') as f:
            f.write(content)
        return str(settings_file)

    def get_settings_xml_path(self, group_id: str) -> Optional[str]:
        """Get path to Maven settings.xml for a group"""
        settings_file = self.settings_dir / f"{group_id}_settings.xml"
        if settings_file.exists():
            return str(settings_file)
        return None

    def list_settings_files(self) -> List[Dict]:
        """List all available settings.xml files in config/settings directory"""
        settings_files = []

        if self.settings_dir.exists():
            for file in self.settings_dir.glob("*.xml"):
                settings_files.append({
                    'name': file.name,
                    'path': str(file),
                    'size': file.stat().st_size
                })

        return settings_files

    def get_settings_file_path(self, filename: str) -> Optional[str]:
        """Get full path for a settings file by name"""
        file_path = self.settings_dir / filename
        if file_path.exists():
            return str(file_path)
        return None