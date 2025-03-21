import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from .base import BaseFile

class LocalFile(BaseFile):
    def __init__(self, settings: Dict):
        super().__init__(settings)
        self.root = Path(settings['root'])
        self.name = settings.get('name', '')
        # Create root directory if it doesn't exist
        self.root.mkdir(parents=True, exist_ok=True)

    def get_uri(self, path: str) -> str:
        abs_path = self.root / path
        return f"file:/{abs_path}"

    def list(self, path: str = "") -> List[Dict]:
        full_path = self.root / path
        items = []
        
        for entry in os.scandir(full_path):
            stat = entry.stat()
            entry_path = f"{path}/{entry.name}" if path else entry.name
            items.append({
                "name": entry.name,
                "uri": self.get_uri(f"{entry_path}"),
                "type": "directory" if entry.is_dir() else "file",
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "size": stat.st_size if entry.is_file() else None
            })
            
        return items

    def get_download_url(self, path: str) -> str:
        return f"/api/storage/download?storage={self.name}&path={path}"

    def get_metadata(self, path: str) -> Dict:
        full_path = self.root / path
        stat = full_path.stat()
        return {
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "size": stat.st_size if full_path.is_file() else None
        }
