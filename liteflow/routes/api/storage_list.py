from flask import jsonify, session, redirect, url_for, request
from ...utils.storage import StorageManager

def init_app(app):
    storage = StorageManager(app.config)
    
    @app.route('/api/storage/<backend>/list', methods=['GET'])
    def list_storage_files(backend):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
            
        path = request.args.get('path', '').lstrip("/")
        try:
            provider = storage.get_backend(backend)
            items = provider.list(path)
            return jsonify({"items": items})
        except Exception as e:
            print(f'Error listing files: {e}')
            return jsonify({"error": str(e)}), 400
