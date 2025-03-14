from flask import jsonify, session, redirect, url_for
from ...utils.storage import StorageManager
from flask_jwt_extended import jwt_required

def init_app(app):
    storage = StorageManager(app.config)
    
    @app.route('/api/storage/backends', methods=['GET'])
    def list_storage_backends():            
        return jsonify({"backends": storage.list_backends()})
