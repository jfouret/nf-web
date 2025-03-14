from flask import render_template, redirect, url_for, session
from ..utils.storage import StorageManager
from flask_jwt_extended import jwt_required

def init_app(app):
    storage_manager = StorageManager(app.config)
    
    @app.route('/storage')
    def storage():
        return render_template('storage.html', backends=storage_manager.list_backends())
