from flask import render_template, redirect, url_for, session, flash, request
import os
import json
import yaml
import shutil
import time
from ..utils.git import fetch_repo_details, checkout_git
from ..utils.file_utils import list_config_files
from markdown import markdown

def init_app(app):
  @app.route('/pipeline/<organization>/<project>', methods=['GET', 'POST'])
  def pipeline_page(organization, project):
    if not session.get('logged_in'):
      return redirect(url_for('login'))

    root_dir = app.config['ROOT_DIR']
    pipelines_path = os.path.join(root_dir, 'pipelines')

    # Get the pipeline details
    pipeline_details = fetch_repo_details(organization, project, pipelines_path)

    # Get the path to the pipeline
    pipeline_dir = os.path.join(pipelines_path, organization, project)

    # Read the nextflow_schema.json
    schema_path = os.path.join(pipeline_dir, 'nextflow_schema.json')
    schema = None
    if os.path.exists(schema_path):
      with open(schema_path, 'r') as f:
        schema = json.load(f)
    else: 
      flash("No schema found")

    # Read README.md
    readme_path = os.path.join(pipeline_dir, 'README.md')
    readme_content = ''
    if os.path.exists(readme_path):
      with open(readme_path, 'r') as f:
        readme_content = f.read()
    else: 
      flash("No schema found")

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
    return render_template('pipeline.html', pipeline=pipeline_details, schema=schema, readme=markdown(readme_content), config_files=config_files)