import os
import re
from typing import Optional
from markdown import markdown
from .git_provider import GitProvider

class GitRepo:
    def __init__(self, provider: GitProvider):
        self.provider = provider
        self.refs = {'branches': {}, 'tags': {}}
                
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
        
    def process_html_content(self, content: str, ref: str) -> str:
        """Process html content to replace relative URLs with raw URLs"""
        pattern = r'(src|href)=[\'"](?!(http|ftp|https):\/\/)([^\'"]+)[\'"]'
        raw_url_base = self.provider.get_raw_file_url("", ref)
        return re.sub(pattern, lambda m: f'{m.group(1)}="{raw_url_base}/{m.group(3)}"', content)

    def fetch_file(self, path: str, ref: str) -> str:
        """Fetch file content using commit SHA with caching"""
        content = self.provider.get_file_content(path, ref)
        return content

    def get_readme_processed(self, ref: str) -> str:
        """Get processed markdown content from repository
        Tries different common markdown filenames"""
        markdown_files = ['README.md', 'Readme.md', 'readme.md']
        
        for filename in markdown_files:
            try:
                content = self.fetch_file(filename, ref)
                processed_content = markdown(content)
                return self.process_html_content(processed_content, ref)
            except:
                continue
        return ""  # Return empty string if no markdown file found

    @property
    def default_branch(self) -> str:
        """Get cache directory for the repository"""
        return self.provider.get_default_branch()
