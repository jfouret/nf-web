from flask import render_template, redirect, url_for, session, flash, request
import os
import json
import yaml
import shutil
import time
from ..utils.github_provider import GitHubProvider
from ..utils.git_repo import GitRepo
from ..utils.pipeline import Pipeline
from ..utils.file_utils import list_config_files
from .. import models
from ..utils.storage import StorageManager
from markdown import markdown

def init_app(app):
  storage_manager = StorageManager(app.config)

  @app.route('/pipeline/<organization>/<project>', methods=['GET', 'POST'])
  def pipeline_page(organization, project):
    
    if not session.get('logged_in'):
      return redirect(url_for('login'))

    root_dir = app.config['ROOT_DIR']
    pipelines_path = os.path.join(root_dir, 'pipelines')

    # Get pipeline from database
    db_pipeline = models.Pipeline.query.filter_by(
      org_name=organization,
      project_name=project
    ).first_or_404()

    try:
      # Initialize provider and repo
      provider = GitHubProvider(organization, project)
      repo = GitRepo(provider, os.path.join(pipelines_path, f"{organization}_{project}"))
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

      # Check required files
      try:
        # Get schema
        schema = json.loads(pipeline.fetch_schema())
        if not schema:
          raise ValueError("Invalid schema format")
        
        # Handle both "definitions" and "$defs" schema formats
        if "definitions" not in schema.keys():
          if "$defs" in schema.keys():
            schema["definitions"] = schema["$defs"]
          elif "defs" in schema.keys():
            schema["definitions"] = schema["defs"]
          else:
            raise ValueError(f"No definitions/$defs/defs key found in schema")
        
        # Get config
        config = pipeline.fetch_config()
        if not config:
          raise ValueError("No nextflow.config found")
        
        # Get README content (optional)
        try:
          readme_content = pipeline.git_repo.fetch_file("README.md", pipeline.commit_sha)
        except Exception:
          readme_content = ''
          
      except Exception as e:
        flash(f'Error loading pipeline: {str(e)}')
        return redirect(url_for('pipelines'))

    except Exception as e:
      flash(f'Error loading pipeline: {str(e)}')
      return redirect(url_for('pipelines'))

    # Get list of configs (from root_dir/configs)
    configs_path = os.path.join(root_dir, 'configs')
    config_files = list_config_files(configs_path)

    # Handle POST request for creating run config
    if request.method == 'POST':
      data = request.get_json()
      run_name = data.get('run_name')
      nextflow_version = data.get('nextflow_version')
      selected_config = data.get('selected_config')
      params_json = data.get('params_json')
      params = json.loads(params_json)

      # Create run config in root_dir/run_configs
      run_configs_path = os.path.join(root_dir, 'run_configs')
      if not os.path.exists(run_configs_path):
        os.makedirs(run_configs_path)

      # Create a directory for the run config
      timestamp = int(time.time())
      run_config_name = f'{run_name}_{timestamp}'
      run_config_dir = os.path.join(run_configs_path, run_config_name)
      os.makedirs(run_config_dir, exist_ok=True)

      # Save params.json
      with open(os.path.join(run_config_dir, 'params.json'), 'w') as f:
        json.dump(params, f)

      # Copy the selected config file to run config dir
      if selected_config:
        source_config_path = os.path.join(configs_path, selected_config)
        dest_config_path = os.path.join(run_config_dir, selected_config)
        shutil.copyfile(source_config_path, dest_config_path)
      else:
        dest_config_path = None

      # Create run.yml with required details
      run_info = {
        'nextflow_version': nextflow_version,
        'date_created': time.strftime('%Y-%m-%d %H:%M:%S'),
        'run_name': run_name,
        'pipeline_name': project,
        'organization': organization,
        'revision': pipeline_details.get('tag') or pipeline_details.get('head'),
        'config_file': selected_config if selected_config else '',
      }

      with open(os.path.join(run_config_dir, 'run.yml'), 'w') as f:
        yaml.dump(run_info, f)

      flash('Run configuration created successfully.', 'success')

      # Redirect to Run Configs page
      return redirect(url_for('run_configs'))

    # Render the template with data
    return render_template('pipeline.html', pipeline=pipeline_details, schema=schema, readme=markdown(readme_content), config_files=config_files, backends=storage_manager.list_backends())
