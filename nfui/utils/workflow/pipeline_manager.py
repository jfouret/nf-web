from pathlib import Path
from typing import Dict, List, Optional
import json
import yaml
import shutil
import time
from .github_provider import GitHubProvider
from .git_repo import GitRepo
from .pipeline import Pipeline
from flask import Flask
from ... import models

class PipelineManager:
    def __init__(self, app: Flask):
        """Initialize PipelineManager
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.root_dir = Path(app.config["ROOT_DIR"])
        self.pipelines_dir = self.root_dir / 'pipelines'
        self.db = models.db
        
    def get_pipeline_path(self, organization: str, project: str) -> Path:
        """Get path for a pipeline directory
        
        Args:
            organization: Organization name
            project: Project name
            
        Returns:
            Path to the pipeline directory
        """
        return self.pipelines_dir / f"{organization}_{project}"
        
    def list_pipelines(self) -> List[Dict]:
        """Get all pipelines with their details
        
        Returns:
            List of pipeline dictionaries with metadata
        """
        pipeline_list = []
        db_pipelines = models.Pipeline.query.all()
        
        for db_pipeline in db_pipelines:
            try:
                provider = GitHubProvider(db_pipeline.org_name, db_pipeline.project_name)
                repo = GitRepo(provider, self.get_pipeline_path(db_pipeline.org_name, db_pipeline.project_name))
                pipeline = Pipeline(repo, db_pipeline.ref, db_pipeline.ref_type)
                
                # Get repository information
                refs = pipeline.get_refs()
                
                # Parse nextflow config
                try:
                    config = pipeline.fetch_config()
                    metadata = pipeline.parse_metadata()
                except Exception:
                    metadata = {}
                
                # Extract branches and tags
                branches = list(refs['branches'].keys())
                tags = list(refs['tags'].keys())
                
                # Get current branch and tag
                current_branch = db_pipeline.ref if db_pipeline.ref_type == 'branch' else branches[0] if branches else None
                current_tag = db_pipeline.ref if db_pipeline.ref_type == 'tag' else None
                
                pipeline_info = {
                    "id": db_pipeline.id,
                    "provider": db_pipeline.provider,
                    "organization": db_pipeline.org_name,
                    "project": db_pipeline.project_name,
                    "description": metadata.get("description", "No description available"),
                    "head": {
                        "sha": refs['branches'].get(current_branch, '')
                    },
                    "branch": current_branch,
                    "tag": current_tag,
                    "branches": branches,
                    "tags": tags,
                    "nextflowVersion": metadata.get("nextflowVersion", "N/A")
                }
                
                pipeline_list.append(pipeline_info)
                
            except Exception:
                # Skip pipelines that can't be loaded
                continue
                
        return pipeline_list
        
    def get_pipeline(self, organization: str, project: str) -> Dict:
        """Get pipeline details
        
        Args:
            organization: Organization name
            project: Project name
            
        Returns:
            Pipeline details dictionary
            
        Raises:
            FileNotFoundError: If pipeline doesn't exist
        """
        db_pipeline = models.Pipeline.query.filter_by(
            org_name=organization,
            project_name=project
        ).first_or_404()
        
        provider = GitHubProvider(organization, project)
        repo = GitRepo(provider, self.get_pipeline_path(organization, project))
        pipeline = Pipeline(repo, db_pipeline.ref, db_pipeline.ref_type)
        
        # Get repository information
        refs = pipeline.git_repo.get_refs()
        
        # Get pipeline details
        pipeline_details = {
            "id": db_pipeline.id,
            "provider": db_pipeline.provider,
            "org": db_pipeline.org_name,
            "name": db_pipeline.project_name,
            "ref": db_pipeline.ref,
            "ref_type": db_pipeline.ref_type,
            "refs": refs
        }
        
        # Get schema and validate
        schema = json.loads(pipeline.fetch_schema())
        if not schema:
            raise ValueError("Invalid schema format")
        
        # Handle both "definitions" and "$defs" schema formats
        if "definitions" not in schema:
            if "$defs" in schema:
                schema["definitions"] = schema["$defs"]
            elif "defs" in schema:
                schema["definitions"] = schema["defs"]
            else:
                raise ValueError("No definitions/$defs/defs key found in schema")
        
        # Get config
        config = pipeline.fetch_config()
        if not config:
            raise ValueError("No nextflow.config found")
        
        # Get README content (optional)
        try:
            readme_content = pipeline.git_repo.fetch_file("README.md", pipeline.commit_sha)
        except Exception:
            readme_content = ''
            
        return {
            "details": pipeline_details,
            "schema": schema,
            "readme": readme_content
        }
        
    def create_run_config(self, run_name: str, pipeline_info: dict, params: dict,
                         nextflow_version: str, selected_config: Optional[str] = None) -> Path:
        """Create a new run configuration
        
        Args:
            run_name: Name of the run
            pipeline_info: Dictionary containing pipeline information
            params: Parameters for the run
            nextflow_version: Version of Nextflow to use
            selected_config: Optional config file to use
            
        Returns:
            Path to the created run config directory
        """
        # Create run config directory
        run_configs_path = self.root_dir / 'run_configs'
        run_configs_path.mkdir(parents=True, exist_ok=True)
        
        # Create unique directory name with timestamp
        timestamp = int(time.time())
        run_config_name = f'{run_name}_{timestamp}'
        run_config_dir = run_configs_path / run_config_name
        run_config_dir.mkdir(exist_ok=True)
        
        # Save params.json
        params_file = run_config_dir / 'params.json'
        with params_file.open('w') as f:
            json.dump(params, f)
        
        # Copy selected config if provided
        if selected_config:
            source_config = self.root_dir / 'configs' / selected_config
            if source_config.exists():
                dest_config = run_config_dir / selected_config
                shutil.copy2(source_config, dest_config)
        
        # Create run.yml
        run_info = {
            'nextflow_version': nextflow_version,
            'date_created': time.strftime('%Y-%m-%d %H:%M:%S'),
            'run_name': run_name,
            'pipeline_name': pipeline_info['name'],
            'organization': pipeline_info['org'],
            'revision': pipeline_info.get('tag') or pipeline_info.get('head'),
            'config_file': selected_config if selected_config else '',
        }
        
        run_yml = run_config_dir / 'run.yml'
        with run_yml.open('w') as f:
            yaml.dump(run_info, f)
            
        return run_config_dir
