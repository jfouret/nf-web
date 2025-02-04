import os
from typing import Optional
from .git_provider import GitProvider

class GitRepo:
    def __init__(self, provider: GitProvider, cache_dir: str):
        self.provider = provider
        self.cache_dir = cache_dir
        self.refs = {'branches': {}, 'tags': {}}
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize refs
        self.update_refs()
        
    def get_refs(self) -> dict:
        """Get repository refs"""
        return self.refs
        
    def update_refs(self) -> None:
        """Update repository refs"""
        self.refs = self.provider.get_refs()
        
    def resolve_ref(self, ref: str, ref_type: str) -> Optional[str]:
        """Convert ref to commit SHA"""
        if ref_type == "commit":
            return ref
        if ref_type == "branch":
            ref_type = "branches"
        elif ref_type == "tag":
            ref_type = "tags"
        elif ref_type not in ["branches", "tags"]:
            raise ValueError(f"Invalid ref type: {ref_type} for {self.provider.org}/{self.provider.project}")
        
        return self.refs[ref_type][ref]
        
    def fetch_file(self, path: str, ref: str) -> str:
        """Fetch file content using commit SHA with caching"""
        cache_path = os.path.join(self.cache_dir, ref, path)
        
        # Check cache first
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return f.read()
                
        # Fetch from provider
        content = self.provider.get_file_content(path, ref)
        
        # Cache the content
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w') as f:
            f.write(content)
            
        return content
