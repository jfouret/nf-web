from github import Github, Auth
from .git_provider import GitProvider
from ..cache import get_or_set_cache
from typing import Dict
from flask import current_app
import requests

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
            auth_token = None
        else:
            auth_token = Auth.Token(token)
        self.token = token
        

        # Initialize GitHub client
        if host != "github.com":
            base_url = f"{protocol}://{host}/api/v3"
            self.gh = Github(base_url=base_url, auth = auth_token)
        else:
            self.gh = Github(auth = auth_token)
            
        # Get repo with caching
        self.repo = get_or_set_cache(
            f"github:repo:{org}:{project}",
            lambda: self.gh.get_repo(f"{org}/{project}")
        )
        
    def get_refs(self) -> Dict[str, Dict[str, str]]:
        cache_key = f"github:refs:{self.org}:{self.project}"
        
        def fetch_refs():
            refs = {
                'branches': {},
                'tags': {},
                'commits': {}
            }
            
            # Get branches
            for branch in self.repo.get_branches():
                refs['branches'][branch.name] = branch.commit.sha
                
            # Get tags
            for tag in self.repo.get_tags():
                refs['tags'][tag.name] = tag.commit.sha

            headers = {
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28'
                }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            response = requests.get(
                url = f"https://api.github.com/repos/{self.org}/{self.project}/commits",
                params = {'per_page': 25, "page": 1},
                headers = headers
            )
            response = response.json()
            commits = [commit["sha"] for commit in response]

            commits.extend(refs['tags'].values())
            commits.extend(refs['branches'].values())
            commits = list(set(commits))
            for commit in commits:
                refs['commits'][commit[:7]] = commit
                
            return refs
            
        return get_or_set_cache(cache_key, fetch_refs)

    def get_default_branch(self) -> str:
        cache_key = f"github:default_branch:{self.org}:{self.project}"
        return get_or_set_cache(
            cache_key,
            lambda: self.repo.default_branch
        )

    def get_raw_file_url(self, path: str, ref: str) -> str:
        """Generate raw file URL for GitHub content"""
        return f"https://raw.githubusercontent.com/{self.org}/{self.project}/{ref}/{path}"

    def get_file_content(self, path: str, ref: str) -> str:
        cache_key = f"github:file:{self.org}:{self.project}:{path}:{ref}"
        
        def fetch_content():
            content = self.repo.get_contents(path, ref=ref)
            return content.decoded_content.decode('utf-8')
            
        return get_or_set_cache(cache_key, fetch_content)
