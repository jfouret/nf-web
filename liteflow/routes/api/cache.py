from flask import jsonify
from ...utils.cache import clear_github_cache, clear_s3_cache

def init_app(app):
    @app.route('/api/cache/clear/github', methods=['POST'])
    def clear_github_cache_endpoint():
        try:
            clear_github_cache()
            return jsonify({"status": "success", "message": "GitHub cache cleared successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/cache/clear/s3', methods=['POST'])
    def clear_s3_cache_endpoint():
        try:
            clear_s3_cache()
            return jsonify({"status": "success", "message": "S3 cache cleared successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
