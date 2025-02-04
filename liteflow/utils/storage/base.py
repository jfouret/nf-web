from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

class BaseFile(ABC):
    def __init__(self, settings: Dict):
        self.settings = settings
        self.type = settings['type']
        self.description = settings.get('description', '')

    @abstractmethod
    def get_uri(self, path: str) -> str:
        """Return full URI (file:// or s3://)"""
        pass

    @abstractmethod
    def list(self, path: str = "") -> List[Dict]:
        """
        List files/directories
        Returns: [{
            "name": str,
            "uri": str,
            "type": "file"|"directory",
            "created": datetime,
            "modified": datetime,
            "size": int
        }]
        """
        pass

    @abstractmethod
    def get_download_url(self, path: str) -> str:
        """Get URL for file download"""
        pass

    @abstractmethod
    def get_metadata(self, path: str) -> Dict:
        """Get file metadata"""
        pass
