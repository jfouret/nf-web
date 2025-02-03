from flask import jsonify, session, redirect, url_for
from ...utils.storage import StorageManager

def init_app(app):
    storage = StorageManager(app.config)
    
    @app.route('/api/storage/backends', methods=['GET'])
    def list_storage_backends():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
            
        return jsonify({"backends": storage.list_backends()})
