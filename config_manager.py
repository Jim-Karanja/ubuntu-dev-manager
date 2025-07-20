"""
Configuration Manager - Handles application settings and preferences
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "ubuntu-dev-manager"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        # Default configuration
        self.default_config = {
            "default_backend": "multipass",
            "default_cpus": 2,
            "default_memory": 2048,
            "default_disk": 10,
            "terminal_emulator": "auto",
            "auto_start_environments": False,
            "log_level": "INFO",
            "theme": "system",
            "window_geometry": {
                "width": 1000,
                "height": 700,
                "x": 100,
                "y": 100
            },
            "multipass": {
                "driver": "qemu",
                "network": "default"
            },
            "lxd": {
                "storage_pool": "default",
                "network": "lxdbr0"
            },
            "templates": {
                "custom_templates_enabled": True,
                "auto_update_templates": False
            }
        }
        
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            return self.default_config.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                
            # Merge with defaults to ensure all keys exist
            config = self.default_config.copy()
            config.update(loaded_config)
            return config
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config file: {e}")
            return self.default_config.copy()
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
    
    def reset(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
    
    def reset_key(self, key: str):
        """Reset a specific key to its default value"""
        keys = key.split('.')
        default_value = self.default_config
        
        for k in keys:
            if isinstance(default_value, dict) and k in default_value:
                default_value = default_value[k]
            else:
                return  # Key doesn't exist in defaults
        
        self.set(key, default_value)
    
    def export_config(self, filepath: str):
        """Export configuration to a file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to export configuration: {e}")
    
    def import_config(self, filepath: str):
        """Import configuration from a file"""
        try:
            with open(filepath, 'r') as f:
                imported_config = json.load(f)
            
            # Merge with current config
            self.config.update(imported_config)
            
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"Failed to import configuration: {e}")
    
    def validate_config(self) -> Dict[str, str]:
        """Validate configuration and return any errors"""
        errors = {}
        
        # Validate backend
        if self.get('default_backend') not in ['multipass', 'lxd']:
            errors['default_backend'] = "Must be 'multipass' or 'lxd'"
        
        # Validate resource values
        cpus = self.get('default_cpus')
        if not isinstance(cpus, int) or cpus < 1 or cpus > 32:
            errors['default_cpus'] = "Must be an integer between 1 and 32"
        
        memory = self.get('default_memory')
        if not isinstance(memory, int) or memory < 512 or memory > 32768:
            errors['default_memory'] = "Must be an integer between 512 and 32768 MB"
        
        disk = self.get('default_disk')
        if not isinstance(disk, int) or disk < 5 or disk > 1000:
            errors['default_disk'] = "Must be an integer between 5 and 1000 GB"
        
        # Validate log level
        if self.get('log_level') not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            errors['log_level'] = "Must be DEBUG, INFO, WARNING, or ERROR"
        
        return errors
    
    def get_backends_config(self) -> Dict[str, Dict[str, Any]]:
        """Get backend-specific configuration"""
        return {
            'multipass': self.get('multipass', {}),
            'lxd': self.get('lxd', {})
        }
    
    def get_window_geometry(self) -> Dict[str, int]:
        """Get window geometry settings"""
        return self.get('window_geometry', self.default_config['window_geometry'])
    
    def set_window_geometry(self, width: int, height: int, x: int, y: int):
        """Set window geometry settings"""
        self.set('window_geometry', {
            'width': width,
            'height': height,
            'x': x,
            'y': y
        })
    
    def get_terminal_preference(self) -> str:
        """Get preferred terminal emulator"""
        return self.get('terminal_emulator', 'auto')
    
    def set_terminal_preference(self, terminal: str):
        """Set preferred terminal emulator"""
        valid_terminals = [
            'auto', 'gnome-terminal', 'konsole', 'xterm', 
            'alacritty', 'wezterm', 'terminator'
        ]
        
        if terminal not in valid_terminals:
            raise ValueError(f"Invalid terminal: {terminal}")
        
        self.set('terminal_emulator', terminal)
