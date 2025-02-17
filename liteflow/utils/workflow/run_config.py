from pathlib import Path
from typing import Dict, List, Optional
import json
import yaml
import shutil
from datetime import datetime
from flask import Flask
from ... import models

class RunConfigManager:
    def __init__(self, app: Flask):
        """Initialize RunConfigManager
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.root_dir = Path(app.config["ROOT_DIR"])
        self.run_configs_dir = self.root_dir / 'run_configs'
        self.db = models.db
        
    def create_run_config(self, organization: str, pipeline_name: str, run_name: str,
                         pipeline_id: int, ref: str, ref_type: str, nextflow_version: str,
                         parameters: dict, config_id: Optional[int] = None) -> Dict:
        """Create a new run configuration
        
        Args:
            organization: Organization name
            pipeline_name: Pipeline project name
            run_name: Name for this run
            pipeline_id: ID of the associated pipeline
            ref: Git reference (branch/tag/commit)
            ref_type: Type of reference ('branch', 'tag', or 'commit')
            nextflow_version: Version of Nextflow to use
            parameters: Pipeline parameters
            config_id: Optional ID of associated config file
            
        Returns:
            Created run config dictionary
            
        Raises:
            ValueError: If run name already exists
        """
        # Check if run name already exists
        if models.RunConfig.query.filter_by(run_name=run_name).first():
            raise ValueError(f"Run configuration with name {run_name} already exists")
            
        # Create directory structure
        run_dir = self.run_configs_dir / organization / pipeline_name / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save params.json
        params_path = run_dir / 'params.yaml'
        with params_path.open('w') as f:
            yaml.dump(parameters, f, indent=2)
            
        # Create run.yml
        run_info = {
            'organization': organization,
            'pipeline_name': pipeline_name,
            'run_name': run_name,
            'ref': ref,
            'ref_type': ref_type,
            'nextflow_version': nextflow_version,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Add config file info if provided
        if config_id:
            config = models.Config.query.get(config_id)
            if config:
                run_info['config_file'] = config.filename
                # Copy config file
                config_src = self.root_dir / 'configs' / config.filename
                if config_src.exists():
                    shutil.copy2(config_src, run_dir / "nextflow.config")
                
        # Create database entry
        run_config = models.RunConfig(
            organization = organization,
            pipeline_name = pipeline_name,
            run_name = run_name,
            pipeline_id = pipeline_id,
            ref = ref,
            ref_type = ref_type,
            nextflow_version = nextflow_version,
            parameters = parameters,
            config_id = config_id
        )
        self.db.session.add(run_config)
        self.db.session.commit()
        
        return run_config._to_dict()
        
    def get_run_config(self, organization: str, pipeline_name: str, run_name: str) -> Dict:
        """Get single run config
        
        Args:
            organization: Organization name
            pipeline_name: Pipeline project name
            run_name: Name of the run
            
        Returns:
            Run config dictionary
            
        Raises:
            FileNotFoundError: If run config doesn't exist
        """
        run_config = models.RunConfig.query.filter_by(
            organization=organization,
            pipeline_name=pipeline_name,
            run_name=run_name
        ).first()
        
        if not run_config:
            raise FileNotFoundError(f"Run config {organization}/{pipeline_name}/{run_name} not found")
            
        return run_config._to_dict()
    
    def get_config_file_from_run_config(self, organization: str, pipeline_name: str, run_name: str) -> str:
        """Get config file from run config

        Args:
            organization: Organization name
            pipeline_name: Pipeline project name
            run_name: Name of the run
        Returns:
           Config file path
        Raises:
            FileNotFoundError: If run config doesn't exist
        """
        run_config = self.get_run_config(organization, pipeline_name, run_name)
        config_file = self.run_configs_dir / organization / pipeline_name / run_name / "nextflow.config"
        if config_file.exists():
            return config_file
        else:
            return None
        
    def list_run_configs(self) -> List[Dict]:
        """Get all run configs
        
        Returns:
            List of run config dictionaries
        """
        run_configs = models.RunConfig.query.all()
        return [run_config._to_dict() for run_config in run_configs]
        
    def delete_run_config(self, organization: str, pipeline_name: str, run_name: str):
        """Delete run config
        
        Args:
            organization: Organization name
            pipeline_name: Pipeline project name
            run_name: Name of the run
            
        Raises:
            FileNotFoundError: If run config doesn't exist
        """
        run_config = models.RunConfig.query.filter_by(
            organization=organization,
            pipeline_name=pipeline_name,
            run_name=run_name
        ).first()
        
        if not run_config:
            raise FileNotFoundError(f"Run config {organization}/{pipeline_name}/{run_name} not found")
            
        # Delete directory if it exists
        run_dir = self.run_configs_dir / organization / pipeline_name / run_name
        if run_dir.exists():
            shutil.rmtree(run_dir)
            
        # Delete database entry
        self.db.session.delete(run_config)
        self.db.session.commit()
