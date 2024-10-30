from flask import request, jsonify, session, redirect, url_for
import os
import yaml
import json
import shutil
import time
from ...utils.git import fetch_repo_details

def init_app(app):
  @app.route('/api/create_run_config', methods=['POST'])
  def create_run_config():
      if not session.get('logged_in'):
          return redirect(url_for('login'))

      data = request.get_json()
      # Extract data from the request
      run_name = data.get('run_name')
      nextflow_version = data.get('nextflow_version')
      selected_config = data.get('selected_config')
      parameters = data.get('parameters')
      organization = data.get('organization')
      project = data.get('project')

      if not all([run_name, nextflow_version, organization, project]):
          return jsonify({'error': 'Missing required fields'}), 400

      # Paths setup
      root_dir = app.config['ROOT_DIR']
      run_configs_path = os.path.join(root_dir, 'run_configs')
      run_config_dir = os.path.join(run_configs_path, organization, project, run_name)
      os.makedirs(run_config_dir, exist_ok=True)

      # Save params.json
      params_json_path = os.path.join(run_config_dir, 'params.json')
      with open(params_json_path, 'w') as f:
          json.dump(parameters, f)

      # Copy selected config file
      if selected_config:
          configs_path = os.path.join(root_dir, 'configs')
          source_config_path = os.path.join(configs_path, selected_config)
          dest_config_path = os.path.join(run_config_dir, selected_config)
          shutil.copyfile(source_config_path, dest_config_path)
      else:
          dest_config_path = ''

      # Fetch pipeline details
      pipelines_path = os.path.join(root_dir, 'pipelines')
      pipeline_details = fetch_repo_details(organization, project, pipelines_path)

      # Create run.yml
      run_info = {
          'nextflow_version': nextflow_version,
          'date_created': time.strftime('%Y-%m-%d %H:%M:%S'),
          'run_name': run_name,
          'pipeline_name': project,
          'organization': organization,
          'revision': pipeline_details.get('tag') or pipeline_details.get('head'),
          'config_file': selected_config if selected_config else '',
      }

      run_yml_path = os.path.join(run_config_dir, 'run.yml')
      with open(run_yml_path, 'w') as f:
          yaml.dump(run_info, f)

      # Update list.csv
      list_csv_path = os.path.join(run_configs_path, 'list.csv')
      if not os.path.exists(list_csv_path):
          with open(list_csv_path, 'w') as f:
              f.write('organization,pipeline_name,run_name\n')
      with open(list_csv_path, 'a') as f:
          f.write(f'{organization},{project},{run_name}\n')

      return jsonify({'message': 'Run configuration created successfully.'}), 200