from flask import redirect, session, url_for, request, jsonify, send_file
from ...utils.storage import StorageManager
from pathlib import Path
from flask_jwt_extended import jwt_required

def init_app(app):
    storage = StorageManager(app.config)
    
    @app.route('/api/storage/download', methods=['GET'])
    def download_storage_file():
            
        if 'storage' not in request.args or 'path' not in request.args:
            return jsonify({"error": "Missing storage or path parameter"}), 400
            
        try:
            storage_name = request.args['storage']
            path = request.args['path'].lstrip('/')  # Remove leading slash
            provider = storage.get_backend(storage_name)
            
            # For local files, serve directly
            if provider.type == 'server':
                file_path = Path(provider.root) / path
                if not file_path.is_file():
                    return jsonify({"error": "File not found"}), 404
                return send_file(file_path, as_attachment=True)
            
            # For other storage types (S3, etc), redirect to URL
            url = provider.get_download_url(path)
            return redirect(url)
            
        except Exception as e:
            print(f'Error generating download URL: {e}')
            return jsonify({"error": str(e)}), 400
