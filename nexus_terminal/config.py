"""Config file management for Nexus Terminal."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / '.nexusterminal'
CONFIG_FILE = CONFIG_DIR / 'config.json'

DEFAULT_CONFIG = {
    'language': 'auto',
    'cloudflared_path': None,
    'custom_commands': {},
}


class ConfigManager:
    """Manages reading and writing the config file at ~/.nexusterminal/config.json."""

    def __init__(self):
        self._config = None

    @property
    def config(self):
        """Lazily load config on first access."""
        if self._config is None:
            self._load()
        return self._config

    def _load(self):
        if not CONFIG_FILE.exists():
            self._create_default()
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            # Ensure all required keys exist (forward compatibility)
            for key, default_val in DEFAULT_CONFIG.items():
                if key not in self._config:
                    self._config[key] = default_val
        except (json.JSONDecodeError, IOError) as e:
            print(f'Config error: {e}')
            self._config = DEFAULT_CONFIG.copy()

    def _create_default(self):
        """Create the config directory and default config file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)

    def save(self):
        """Persist config to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        """Get a top-level config value."""
        return self.config.get(key, default)

    def get_custom_command(self, prefix):
        """Get a custom command by prefix. Returns dict or None."""
        return self.config.get('custom_commands', {}).get(prefix)

    def add_custom_command(self, prefix, command, description=''):
        """Add or update a custom command."""
        if 'custom_commands' not in self.config:
            self.config['custom_commands'] = {}
        self.config['custom_commands'][prefix] = {
            'command': command,
            'description': description,
        }
        self.save()

    def get_all_custom_commands(self):
        """Return all custom commands dict."""
        return self.config.get('custom_commands', {})
