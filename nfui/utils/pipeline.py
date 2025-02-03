from typing import Dict, Optional
from .git_repo import GitRepo

class Pipeline:
    def __init__(self, git_repo: GitRepo, release: str = None, release_type: str = None):
        self.git_repo = git_repo
        self.release = release
        self.release_type = release_type
        
        # Initialize commit_sha as None
        self.commit_sha = None
        
        # Update refs on init
        self.git_repo.update_refs()
        
        # If no release specified, try to use default branch
        if not (release and release_type):
            refs = self.get_refs()
            if 'main' in refs['branches']:
                self.release = 'main'
                self.release_type = 'branch'
            elif 'master' in refs['branches']:
                self.release = 'master'
                self.release_type = 'branch'
            else:
                raise ValueError("No default branch (main/master) found")
        
        # Resolve release to commit SHA
        if not self.commit_sha:
            self.commit_sha = self.git_repo.resolve_ref(self.release, self.release_type)
            if not self.commit_sha:
                raise ValueError(f"Could not resolve ref {self.release} of type {self.release_type}")
            
    def get_refs(self) -> Dict[str, Dict[str, str]]:
        """Get repository refs"""
        return self.git_repo.get_refs()
        
    def get_default_branch(self) -> tuple[str, str]:
        """Get default branch name and type"""
        refs = self.get_refs()
        if 'main' in refs['branches']:
            return 'main', 'branch'
        elif 'master' in refs['branches']:
            return 'master', 'branch'
        raise ValueError("No default branch (main/master) found")
        
    def fetch_config(self) -> str:
        """Get nextflow.config content"""
        if not self.commit_sha:
            raise ValueError("No commit SHA available. Initialize with valid release and release_type.")
        return self.git_repo.fetch_file("nextflow.config", self.commit_sha)
        
    def parse_metadata(self) -> dict:
        """Parse nextflow.config for metadata"""
        config = self.fetch_config()
        # TODO: Implement config parsing
        return {}
        
    def fetch_schema(self) -> str:
        """Get nextflow_schema.json content"""
        if not self.commit_sha:
            raise ValueError("No commit SHA available. Initialize with valid release and release_type.")
        return self.git_repo.fetch_file("nextflow_schema.json", self.commit_sha)
