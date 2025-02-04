from flask import render_template, redirect, url_for, session
from ..utils.storage import StorageManager

def init_app(app):
    storage_manager = StorageManager(app.config)
    
    @app.route('/storage')
    def storage():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return render_template('storage.html', backends=storage_manager.list_backends())
