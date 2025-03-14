from typing import Dict, List
from pathlib import Path
from .base import BaseFile
from .local import LocalFile
from .s3 import S3File
from ...config import Config

class StorageManager:
    def __init__(self, app_config):
        self.backends = {}
        
        # Load storage backends using the static method
        storage_backends = Config.load_storage_backends(
            app_config['STORAGE_BACKEND_CONFIG'],
            app_config['ROOT_DIR']
        )
        
        for name, settings in storage_backends.items():
            settings = settings.copy()  # Create a copy to avoid modifying the original
            settings['name'] = name  # Add backend name to settings
            if settings['type'] == 'local':
                self.backends[name] = LocalFile(settings)
            elif settings['type'] == 's3':
                self.backends[name] = S3File(settings)

    def get_backend(self, name: str) -> BaseFile:
        return self.backends[name]

    def list_backends(self) -> List[Dict]:
        return [
            {
                "name": name,
                "type": backend.type,
                "description": backend.description
            }
            for name, backend in self.backends.items()
        ]
