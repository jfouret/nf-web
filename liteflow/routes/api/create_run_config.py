from flask import jsonify, request
from ... import models
from ...utils.workflow.run_config import RunConfigManager

def init_app(app):
    run_config_manager = RunConfigManager(app)

    @app.route('/api/create_run_config', methods=['POST'])
    def create_run_config():
        try:
            data = request.get_json()
            
            # Get pipeline
            pipeline = models.Pipeline.query.filter_by(
                org_name=data['organization'],
                project_name=data['project']
            ).first()
            
            if not pipeline:
                return jsonify({'error': 'Pipeline not found'}), 404
                
            # Get config if selected
            config_id = None
            if data.get('selected_config'):
                config = models.Config.query.filter_by(filename=data['selected_config']).first()
                if config:
                    config_id = config.id
                    
            # Create run config
            run_config = run_config_manager.create_run_config(
                organization=data['organization'],
                pipeline_name=data['project'],
                run_name=data['run_name'],
                pipeline_id=pipeline.id,
                ref=data['ref'],
                ref_type=data['ref_type'],
                nextflow_version=data['nextflow_version'],
                parameters=data['parameters'],
                config_id=config_id
            )
            
            return jsonify({'message': 'Run configuration created successfully'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
