from github import Github
from .git_provider import GitProvider
from .cache import github_cache
from typing import Dict
from flask import current_app

class GitHubProvider(GitProvider):
    def __init__(self, org: str, project: str, host: str = "github.com", protocol: str = "https"):
        self.org = org
        self.project = project
        self.host = host
        self.protocol = protocol
        
        # Get token from config
        token = current_app.config['GITHUB_TOKEN']
        if token == "":
            token = None
        
        # Initialize GitHub client
        if host != "github.com":
            base_url = f"{protocol}://{host}/api/v3"
            self.gh = Github(base_url=base_url, login_or_token=token)
        else:
            self.gh = Github(login_or_token=token)
            
        self.repo = self.gh.get_repo(f"{org}/{project}")
        
    @github_cache
    def get_refs(self) -> Dict[str, Dict[str, str]]:
        refs = {
            'branches': {},
            'tags': {}
        }
        
        # Get branches
        for branch in self.repo.get_branches():
            refs['branches'][branch.name] = branch.commit.sha
            
        # Get tags
        for tag in self.repo.get_tags():
            refs['tags'][tag.name] = tag.commit.sha
            
        return refs
    
    @github_cache
    def get_file_content(self, path: str, ref: str) -> str:
        content = self.repo.get_contents(path, ref=ref)
        return content.decoded_content.decode('utf-8')
