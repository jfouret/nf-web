from flask import render_template, redirect, url_for, session, flash
import os
from ..utils.git import fetch_repo_details, checkout_git
from ..utils.nf import parse_nf_manifest

def init_app(app):
    @app.route('/pipelines')    
    def pipelines():
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        root_dir = app.config['ROOT_DIR']
        pipelines_path = os.path.join(root_dir, 'pipelines')
        pipelines = []
        if os.path.exists(pipelines_path):
            for org in os.listdir(pipelines_path):
                org_path = os.path.join(pipelines_path, org)
                if not os.path.isdir(org_path):
                    continue
                for repo in os.listdir(org_path):
                    repo_path = os.path.join(org_path, repo)
                    if not os.path.isdir(repo_path):
                        continue
                    info = fetch_repo_details(org, repo, pipelines_path)
                    res = parse_nf_manifest(os.path.join(repo_path,info["head"]["sha"],"nextflow.config"))
                    info["nextflowVersion"] = res["nextflowVersion"]
                    info["description"] = res["description"]
                    pipelines.append(info)

        return render_template('pipelines.html', pipelines=pipelines)
