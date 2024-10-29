from flask import render_template, request, redirect, url_for, session, flash
from git import Repo
import os
from ..utils.git import checkout_git

def init_app(app):
    @app.route('/import_pipeline', methods=['GET', 'POST'])
    def import_pipeline():
        if not session.get('logged_in'):
            return redirect(url_for('login'))

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
                checkout_git("main", organization, pipeline_name, pipelines_path)
            except Exception as error1:
                try:
                    checkout_git("master", organization, pipeline_name, pipelines_path)
                except  Exception as error2:
                    flash('Error checking out repository.')
                    print("Error checking out repository.")
                    print(error1)
                    print(error2)
                    return redirect(url_for('import_pipeline'))

        return render_template('import_pipeline.html')
