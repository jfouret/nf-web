from flask import render_template, redirect, url_for, session, flash
import os
from ..utils.github_provider import GitHubProvider
from ..utils.git_repo import GitRepo
from ..utils.pipeline import Pipeline
from .. import models

def init_app(app):
  @app.route('/pipelines')  
  def pipelines():
    if not session.get('logged_in'):
      return redirect(url_for('login'))

    root_dir = app.config['ROOT_DIR']
    pipelines_path = os.path.join(root_dir, 'pipelines')
    pipeline_list = []

    # Get all pipelines from database
    db_pipelines = models.Pipeline.query.all()
    
    for db_pipeline in db_pipelines:
      provider = GitHubProvider(db_pipeline.org_name, db_pipeline.project_name)
      repo = GitRepo(provider, os.path.join(pipelines_path, f"{db_pipeline.org_name}_{db_pipeline.project_name}"))
      pipeline = Pipeline(repo, db_pipeline.ref, db_pipeline.ref_type)
      
      # Get repository information
      refs = pipeline.get_refs()
      
      # Parse nextflow config
      try:
        config = pipeline.fetch_config()
        metadata = pipeline.parse_metadata()
      except Exception as e:
        config = None
        metadata = {}
      
      # Extract branches and tags from refs
      branches = list(refs['branches'].keys())
      tags = list(refs['tags'].keys())
      
      # Get current branch and tag
      current_branch = db_pipeline.ref if db_pipeline.ref_type == 'branch' else branches[0] if branches else None
      current_tag = db_pipeline.ref if db_pipeline.ref_type == 'tag' else None
      
      pipeline_info = {
        "id": db_pipeline.id,
        "provider": db_pipeline.provider,
        "organization": db_pipeline.org_name,
        "project": db_pipeline.project_name,
        "description": metadata.get("description", "No description available"),
        "head": {
          "sha": refs['branches'].get(current_branch, '')
        },
        "branch": current_branch,
        "tag": current_tag,
        "branches": branches,
        "tags": tags,
        "nextflowVersion": metadata.get("nextflowVersion", "N/A")
      }
      
      pipeline_list.append(pipeline_info)
        
    return render_template('pipelines.html', pipelines=pipeline_list)
