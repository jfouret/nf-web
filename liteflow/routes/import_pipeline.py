from flask import render_template, request, redirect, url_for, session, flash, jsonify, make_response
import os
from ..utils.workflow.github_provider import GitHubProvider
from ..utils.workflow.git_repo import GitRepo
from .. import models
from flask_jwt_extended import jwt_required
from pathlib import Path

def init_app(app):
    @app.route('/import_pipeline', methods=['GET', 'POST'])
    def import_pipeline():
        if request.method == 'POST':
            if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                app.logger.error('Invalid POST request to /import_pipeline. Missing X-Requested-With=XMLHttpRequest header.')
                return jsonify({'error': 'Invalid request'}), 400
            repo_data = request.form['repository'].split('/')
            if len(repo_data) != 2:
                error_msg = 'Invalid repository format. Use "organization/pipeline_name".'
                return jsonify({'error': error_msg}), 400
            
            root_dir = Path(app.config['ROOT_DIR'])
            pipelines_path = root_dir / 'pipelines'
            pipelines_path.mkdir(parents=True, exist_ok=True)

            organization, pipeline_name = repo_data
            
            try:
                existing_pipeline = models.Pipeline.query.filter_by(
                    org_name=organization,
                    project_name=pipeline_name
                ).first()
                
                if existing_pipeline:
                    success_msg = 'Pipeline already imported.'
                    response = jsonify({'success': True, 'message': success_msg})
                    flash(success_msg)
                    return response
                
                # Initialize provider and repo
                provider = GitHubProvider(organization, pipeline_name)
                repo = GitRepo(provider)
                repo.update_refs()
                
                # Create new pipeline record
                new_pipeline = models.Pipeline(
                    provider='github',
                    org_name=organization,
                    project_name=pipeline_name
                )
                
                models.db.session.add(new_pipeline)
                models.db.session.commit()
                
                success_msg = 'Pipeline imported successfully.'
                response = jsonify({'success': True, 'message': success_msg})
                flash(success_msg)
                return response

            except Exception as e:
                error_msg = f'Error importing pipeline: {str(e)}'
                app.logger.error(error_msg)
                flash(error_msg)
                return jsonify({'error': error_msg}), 500

        return render_template('import_pipeline.html')
