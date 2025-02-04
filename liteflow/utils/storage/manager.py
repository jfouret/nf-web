from typing import Dict, List
from .base import BaseFile
from .server import ServerFile
from .s3 import S3File

class StorageManager:
    def __init__(self, config):
        self.backends = {}
        for name, settings in config['STORAGE_BACKENDS'].items():
            settings = settings.copy()  # Create a copy to avoid modifying the original
            settings['name'] = name  # Add backend name to settings
            if settings['type'] == 'server':
                self.backends[name] = ServerFile(settings)
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
