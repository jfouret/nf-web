from abc import ABC, abstractmethod
from typing import Dict, Optional

class GitProvider(ABC):
    """Abstract base class for Git providers"""
    
    @abstractmethod
    def __init__(self, org: str, project: str, host: str = "github.com", protocol: str = "https"):
        pass
        
    @abstractmethod
    def get_refs(self) -> Dict[str, Dict[str, str]]:
        """
        Get repository refs
        Returns: {
            'branches': {name: sha, ...},
            'tags': {name: sha, ...}
        }
        """
        pass
        
    @abstractmethod
    def get_file_content(self, path: str, ref: str) -> str:
        """Get file content at specific ref"""
        pass
