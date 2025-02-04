from flask import render_template, redirect, url_for, session
from ..utils.workflow.pipeline_manager import PipelineManager

def init_app(app):
    pipeline_manager = PipelineManager(app)

    @app.route('/pipelines')  
    def pipelines():
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        pipeline_list = pipeline_manager.list_pipelines()
        return render_template('pipelines.html', pipelines=pipeline_list)
