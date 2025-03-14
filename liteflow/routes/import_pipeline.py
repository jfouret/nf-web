from flask import render_template, request, redirect, url_for, session, flash
import os
from ..utils.workflow.github_provider import GitHubProvider
from ..utils.workflow.git_repo import GitRepo
from .. import models
from flask_jwt_extended import jwt_required

def init_app(app):
    @app.route('/import_pipeline', methods=['GET', 'POST'])
    def import_pipeline():
        if request.method == 'POST':
            repo_data = request.form['repository'].split('/')
            if len(repo_data) != 2:
                flash('Invalid repository format. Use "organization/pipeline_name".')
                return redirect(url_for('import_pipeline'))
            
            root_dir = app.config['ROOT_DIR']
            pipelines_path = os.path.join(root_dir, 'pipelines')

            if not os.path.exists(root_dir):
                os.makedirs(root_dir)
            if not os.path.exists(pipelines_path):
                os.makedirs(pipelines_path)

            organization, pipeline_name = repo_data
            
            try:
                # Check if pipeline already exists
                existing_pipeline = models.Pipeline.query.filter_by(
                    org_name=organization,
                    project_name=pipeline_name
                ).first()
                
                if existing_pipeline:
                    flash('Pipeline already imported.')
                    return redirect(url_for('pipelines'))
                
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
                
                flash('Pipeline imported successfully.')
                return redirect(url_for('pipelines'))
                
            except Exception as e:
                flash(f'Error importing pipeline: {str(e)}')
                return redirect(url_for('import_pipeline'))

        return render_template('import_pipeline.html')
