from flask import render_template, redirect, url_for, session, flash
from ..utils.workflow import RunConfigManager

def init_app(app):
    run_config_manager = RunConfigManager(app)

    @app.route('/run_config/<organization>/<pipeline>/<run_name>')
    def run_config_detail(organization, pipeline, run_name):
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        try:
            run_config = run_config_manager.get_run_config(organization, pipeline, run_name)
            return render_template(
                'run_config.html',
                run_info={
                    'organization': run_config['organization'],
                    'pipeline_name': run_config['pipeline_name'],
                    'run_name': run_config['run_name'],
                    'ref': run_config['ref'],
                    'ref_type': run_config['ref_type'],
                    'nextflow_version': run_config['nextflow_version'],
                    'config_file': run_config.get('config_id')
                },
                params=run_config['parameters']
            )
        except FileNotFoundError:
            flash('Run configuration not found.', 'error')
            return redirect(url_for('run_configs'))
        except Exception as e:
            flash(f'Error loading run configuration: {str(e)}', 'error')
            return redirect(url_for('run_configs'))
