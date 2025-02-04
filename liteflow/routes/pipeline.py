from flask import render_template, redirect, url_for, session, flash, request
import json
from markdown import markdown
from ..utils.workflow.pipeline_manager import PipelineManager
from ..utils.storage import StorageManager
from ..utils.workflow.config import ConfigManager

def init_app(app):
    storage_manager = StorageManager(app.config)
    pipeline_manager = PipelineManager(app)
    config_manager = ConfigManager(app)

    @app.route('/pipeline/<organization>/<project>', methods=['GET', 'POST'])
    def pipeline_page(organization: str, project: str):
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        try:
            # Get pipeline details
            pipeline_data = pipeline_manager.get_pipeline(organization, project)
            
            # Get list of configs
            all_configs = config_manager.list_configs()

            # Handle POST request for creating run config
            if request.method == 'POST':
                try:
                    data = request.get_json()
                    pipeline_manager.create_run_config(
                        run_name=data.get('run_name'),
                        pipeline_info=pipeline_data['details'],
                        params=json.loads(data.get('params_json')),
                        nextflow_version=data.get('nextflow_version'),
                        selected_config=data.get('selected_config')
                    )

                    flash('Run configuration created successfully.', category='success')
                    return redirect(url_for('run_configs'))
                    
                except Exception as e:
                    flash(f'Error creating run configuration: {str(e)}', category='error')
                    return redirect(url_for('pipeline_page', organization=organization, project=project))

            # Render the template with data
            return render_template(
                'pipeline.html',
                pipeline=pipeline_data['details'],
                schema=pipeline_data['schema'],
                readme=markdown(pipeline_data['readme']),
                config_files=all_configs,
                backends=storage_manager.list_backends()
            )

        except Exception as e:
            flash(f'Error loading pipeline: {str(e)}', category='error')
            return redirect(url_for('pipelines'))
