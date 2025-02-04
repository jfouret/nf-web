from flask import render_template, redirect, url_for, session, flash
import os
import yaml
import json

def init_app(app):
  @app.route('/run_config/<organization>/<pipeline>/<run_name>')
  def run_config_detail(organization, pipeline, run_name):
    if not session.get('logged_in'):
      return redirect(url_for('login'))

    root_dir = app.config['ROOT_DIR']
    run_config_dir = os.path.join(root_dir, 'run_configs', organization, pipeline, run_name)
    run_yml_path = os.path.join(run_config_dir, 'run.yml')
    params_json_path = os.path.join(run_config_dir, 'params.json')
    config_content = ''

    if not os.path.exists(run_yml_path) or not os.path.exists(params_json_path):
      flash('Run configuration files are missing.', 'error')
      return redirect(url_for('run_configs'))

    # Load run.yml
    with open(run_yml_path, 'r') as f:
      run_info = yaml.safe_load(f)

    # Load params.json
    with open(params_json_path, 'r') as f:
      params = json.load(f)

    # Load config file content if exists
    config_file = run_info.get('config_file')
    if config_file:
      config_file_path = os.path.join(run_config_dir, config_file)
      if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
          config_content = f.read()

    return render_template('run_config.html', run_info=run_info, params=params, config_content=config_content)