"""
Configuration management.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Config:
    """Configuration manager."""

    DEFAULT_CONFIG = {
        'file_extensions': {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic'],
            'videos': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
        },
        'organize': {
            'mode': 'year_month',
            'remove_duplicates': False,
            'dry_run': True
        },
        'logging': {
            'level': 'INFO',
            'file': 'media_organiser.log',
            'console': True
        },
        'date_extraction': {
            'prefer_exif': True,
            'fallback_to_filename': True,
            'fallback_to_mtime': True
        },
        'advanced': {
            'hash_algorithm': 'sha256',
            'secure_delete': False,
            'create_backup': False
        }
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path
        self.data = self.DEFAULT_CONFIG.copy()

        if config_path and config_path.exists():
            self.load(config_path)

    def load(self, config_path: Path):
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file
        """
        try:
            config_path = Path(config_path)

            if config_path.suffix == '.json':
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
            elif config_path.suffix in ['.yaml', '.yml']:
                with open(config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")

            # Merge with defaults
            self._merge_config(loaded_config)
            logger.info(f"Loaded configuration from: {config_path}")

        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {str(e)}")
            logger.info("Using default configuration")

    def save(self, config_path: Path):
        """
        Save configuration to file.

        Args:
            config_path: Path to save configuration
        """
        try:
            config_path = Path(config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            if config_path.suffix == '.json':
                with open(config_path, 'w') as f:
                    json.dump(self.data, f, indent=2)
            elif config_path.suffix in ['.yaml', '.yml']:
                with open(config_path, 'w') as f:
                    yaml.dump(self.data, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")

            logger.info(f"Saved configuration to: {config_path}")

        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Dot-separated key (e.g., 'organize.mode')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Dot-separated key (e.g., 'organize.mode')
            value: Value to set
        """
        keys = key.split('.')
        data = self.data

        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def _merge_config(self, new_config: Dict):
        """Merge new configuration with existing."""

        def merge_dict(base: Dict, new: Dict):
            for key, value in new.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value

        merge_dict(self.data, new_config)

    def reset(self):
        """Reset to default configuration."""
        self.data = self.DEFAULT_CONFIG.copy()