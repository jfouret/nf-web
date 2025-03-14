from flask import render_template, redirect, url_for, session, flash
from ..utils.workflow.run_config import RunConfigManager
from flask_jwt_extended import jwt_required

def init_app(app):
    run_config_manager = RunConfigManager(app)

    @app.route('/run_configs')
    def run_configs():

        try:
            run_configs = run_config_manager.list_run_configs()
            return render_template('run_configs.html', run_configs=run_configs)
        except Exception as e:
            flash(f'Error loading run configurations: {str(e)}', 'error')
            return render_template('run_configs.html', run_configs=[])
