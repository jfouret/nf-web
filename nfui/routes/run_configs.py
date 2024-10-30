from flask import render_template, redirect, url_for, session, flash
import os
import csv
import yaml
import json

def init_app(app):
  @app.route('/run_configs')
  def run_configs():
      if not session.get('logged_in'):
          return redirect(url_for('login'))

      root_dir = app.config['ROOT_DIR']
      run_configs_path = os.path.join(root_dir, 'run_configs')
      list_csv_path = os.path.join(run_configs_path, 'list.csv')

      run_configs = []

      if os.path.exists(list_csv_path):
          with open(list_csv_path, 'r') as csvfile:
              reader = csv.DictReader(csvfile)
              for row in reader:
                  organization = row['organization']
                  pipeline_name = row['pipeline_name']
                  run_name = row['run_name']
                  run_config_dir = os.path.join(run_configs_path, organization, pipeline_name, run_name)
                  run_yml_path = os.path.join(run_config_dir, 'run.yml')
                  if os.path.exists(run_yml_path):
                      with open(run_yml_path, 'r') as f:
                          run_info = yaml.safe_load(f)
                      run_configs.append({
                          'organization': organization,
                          'pipeline_name': pipeline_name,
                          'run_name': run_name,
                          'revision': run_info.get('revision', ''),
                          'nextflow_version': run_info.get('nextflow_version', ''),
                          'config_file': run_info.get('config_file', '')
                      })
      else:
          flash('No run configurations found.', 'warning')

      return render_template('run_configs.html', run_configs=run_configs)