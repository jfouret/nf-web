from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil
from datetime import datetime
from ...utils.file_utils import get_file_digest
from flask import Flask
from ... import models

class ConfigManager:
    def __init__(self, app: Flask, at_app_creation: bool = False):
        """Initialize ConfigManager and handle default config
        
        Args:
            app: Flask application instance
            at_app_creation: Whether this is being initialized during app creation
        """
        self.app = app
        self.root_dir = Path(app.config["ROOT_DIR"])
        self.configs_dir = self.root_dir / 'configs'
        self.db = models.db
        
        # Only handle default config during app creation
        if at_app_creation and app.config.get('DEFAULT_CONFIG'):
            enforced_path = Path(app.config['DEFAULT_CONFIG'])
            if enforced_path.exists():
                try:
                    self.enforce_default_config(enforced_path)
                except RuntimeError as e:
                    raise RuntimeError(f"Error enforcing default config: {str(e)}")
    
    @property
    def has_enforced_default(self) -> bool:
        """Check if there is an enforced default config"""
        return bool(self.app.config.get('DEFAULT_CONFIG'))
        
    def get_config_path(self, filename: str) -> Path:
        """Get path for a config file
        
        Args:
            filename: Name of the config file
            
        Returns:
            Path to the config file
        """
        if not filename.endswith('.config'):
            filename += '.config'
        return self.configs_dir / filename
        
    def list_configs(self) -> List[Dict]:
        """Get all configs
        
        Returns:
            List of config dictionaries
        """
        configs = models.Config.query.all()
        return [config._to_dict() for config in configs]
        
    def get_config(self, filename: str) -> Dict:
        """Get single config by filename
        
        Args:
            filename: Name of the config file
            
        Returns:
            Config dictionary
            
        Raises:
            FileNotFoundError: If config doesn't exist
        """
        config = models.Config.query.filter_by(filename=filename).first()
        if not config:
            raise FileNotFoundError(f"Config {filename} not found")
        return config._to_dict()
        
    def create_config(self, name: str, filename: str) -> Dict:
        """Create a new config
        
        Args:
            name: Display name for the config
            filename: Name of the config file
            
        Returns:
            Created config dictionary
            
        Raises:
            ValueError: If config with filename already exists
        """
        
        if not filename.endswith('.config'):
            filename += '.config'
            
        # Check if config already exists
        if models.Config.query.filter_by(filename=filename).first():
            raise ValueError(f"Config with filename {filename} already exists")
            
        # Create config file
        config_path = self.get_config_path(filename)
        with config_path.open('w') as f:
            f.write('')
            
        # Create database entry
        config = models.Config._create(name=name, filename=filename)
        self.db.session.add(config)
        self.db.session.commit()
        
        return config._to_dict()
        
    def update_config(self, filename: str, content: str):
        """Update config content
        
        Args:
            filename: Name of the config file
            content: New content for the config
            
        Raises:
            FileNotFoundError: If config doesn't exist
        """
        
        config = models.Config.query.filter_by(filename=filename).first()
        if not config:
            raise FileNotFoundError(f"Config {filename} not found")
            
        # Update file
        config_path = self.get_config_path(filename)
        with config_path.open('w') as f:
            f.write(content)
            
        # Update timestamp
        config.updated_at = datetime.utcnow()
        self.db.session.commit()
        
    def delete_config(self, filename: str):
        """Delete config
        
        Args:
            filename: Name of the config file
            
        Raises:
            FileNotFoundError: If config doesn't exist
            ValueError: If trying to delete enforced default config
        """
        
        config = models.Config.query.filter_by(filename=filename).first()
        if not config:
            raise FileNotFoundError(f"Config {filename} not found")
            
        # Delete file if it exists
        config_path = self.get_config_path(filename)
        if config_path.exists():
            config_path.unlink()
            
        # Delete database entry
        self.db.session.delete(config)
        self.db.session.commit()
        
    def set_default(self, filename: str):
        """Set config as default
        
        Args:
            filename: Name of the config file
            
        Raises:
            FileNotFoundError: If config doesn't exist
        """
        
        config = models.Config.query.filter_by(filename=filename).first()
        if not config:
            raise FileNotFoundError(f"Config {filename} not found")
            
        models.Config.set_default(config.id)
        self.db.session.commit()
        
    def get_default(self) -> Optional[Dict]:
        """Get default config
        
        Returns:
            Default config dictionary or None if no default exists
        """
        config = models.Config.get_default()
        return config._to_dict() if config else None
        
    def check_default_config(self, enforced_path: Path) -> Tuple[bool, bool]:
        """Check if default config exists and matches enforced config
        
        Args:
            enforced_path: Path to enforced config file
            
        Returns:
            Tuple of (exists, matches)
        """
        default_path = self.configs_dir / 'default.config'
        if not default_path.exists():
            return False, None
        default_digest = get_file_digest(default_path)
        enforced_digest = get_file_digest(enforced_path)
        return True, default_digest == enforced_digest
        
    def enforce_default_config(self, enforced_path: Path):
        """Copy enforced config and create database entry
        
        Args:
            enforced_path: Path to enforced config file
            
        Raises:
            RuntimeError: If default config exists but differs
        """
        
        exists, matches = self.check_default_config(enforced_path)
        if exists and not matches:
            raise RuntimeError("Existing default.config differs from enforced default config!")
        elif not exists:
            dst_path = self.configs_dir / 'default.config'
            shutil.copy2(enforced_path, dst_path)
            
            config = models.Config._create(
                name='Default Configuration',
                filename='default.config',
                is_default=True
            )
            self.db.session.add(config)
            self.db.session.commit()
