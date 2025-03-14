from flask import render_template, redirect, url_for, session, flash, request
import json
from markdown import markdown
from ..utils.storage import StorageManager
from ..utils.workflow.config import ConfigManager
from ..utils.workflow import RunConfigManager
from ..utils.workflow import GitHubProvider
from ..utils.workflow import GitRepo
from ..utils.workflow import Pipeline
from flask_jwt_extended import jwt_required

def init_app(app):
    storage_manager = StorageManager(app.config)
    config_manager = ConfigManager(app)
    run_config_manager = RunConfigManager(app)

    @app.route('/pipeline/<organization>/<project>/<ref_type>/<ref>', methods=['GET', 'POST'])
    def pipeline_page(organization: str, project: str, ref_type: str, ref: str):

        # Validate ref_type
        provider = GitHubProvider(organization, project)
        repo = GitRepo(provider)
        pipeline_data = Pipeline(repo)

        if ref_type not in ['branch', 'tag', 'commit']:
            flash('Invalid reference type', 'error')
            return redirect(url_for('pipelines'))
        
        refs = repo.get_refs()
        
        if ref_type == 'branch':
            commit_sha = refs["branches"][ref]
        elif ref_type == 'tag':
            commit_sha = refs["tags"][ref]
        elif ref_type == 'commit':
            commit_sha = refs["commits"][ref]

        # Get list of configs
        all_configs = config_manager.list_configs()

        # Handle POST request for creating run config
        if request.method == 'POST':
            try:
                data = request.get_json()
                run_config_manager.create_run_config(
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

        # Render the template with data
        schema = json.loads(repo.fetch_file('nextflow_schema.json', commit_sha))
        if not "definitions" in schema.keys():
            if "defs" in schema.keys():
                schema["definitions"] = schema["defs"]
            elif "$defs" in schema.keys():
                schema["definitions"] = schema["$defs"]
            else:
                schema["definitions"] = {}
        metadata = pipeline_data.parse_metadata()
        return render_template(
            'pipeline.html',
            pipeline = {
                "organization": organization,
                "project": project,
                "name": f"{organization}/{project}",
                "nextflowVersion": metadata['nextflowVersion'],
                "head": commit_sha[:7],
                "description": metadata["description"]
            },
            branches=refs["branches"],
            tags=refs["tags"],
            commits=refs["commits"],
            schema=schema,
            readme=repo.get_readme_processed(commit_sha),
            config_files=all_configs,
            backends=storage_manager.list_backends(),
            ref=ref,
            ref_type=ref_type
        )
