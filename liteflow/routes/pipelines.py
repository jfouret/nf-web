from flask import render_template, redirect, url_for, session
from .. import models
from ..utils.workflow import GitHubProvider
from ..utils.workflow import GitRepo
from ..utils.workflow import Pipeline

def init_app(app):
    @app.route('/pipelines')  
    def pipelines():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        pipeline_list = []
        
        for item in models.Pipeline.query.all():
            # Create Git provider for each pipeline
            if item.provider == 'github':
                provider = GitHubProvider(item.org_name, item.project_name)
            else:
                raise ValueError(f"Unsupported provider: {item.provider}")
            repo = GitRepo(provider)
            default_branch = repo.default_branch
            pipeline = Pipeline(repo, default_branch, 'branch')
            metadata = pipeline.parse_metadata()
            # Get Git information including refs mapping
            refs = provider.get_refs()
            pipeline_info = {
                'organization': item.org_name,
                'project': item.project_name,
                'description': metadata['description'],
                'tag': None,  # Will be set by frontend when user selects
                'branch': default_branch,  # GitHub's default branch
                'commit': refs['branches'][default_branch][:7],
                'ref_type': 'branch',  # Default to branch
                'refs': {  # Mapping of refs to commit SHAs
                    'branches': refs['branches'],
                    'tags': refs['tags'],
                    'commits': refs['commits']
                },
                'default_branch': default_branch
            }
            pipeline_list.append(pipeline_info)

        return render_template('pipelines.html', pipelines=pipeline_list)
