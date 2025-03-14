from flask import Flask, send_from_directory, redirect, url_for, jsonify, request
from pathlib import Path
from .utils.workflow import ConfigManager
from dotenv import load_dotenv
from .config import Config
from . import models
from .utils.cache import init_cache
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta
import json
import os

def create_app():
    app = Flask('liteflow')
    load_dotenv()
    app.config.from_object(Config)

    # Initialize database
    models.db.init_app(app)
    with app.app_context():
        models.db.create_all()
        
    # Initialize cache
    init_cache(app)
    
    # Configure JWT
    app.config["JWT_SECRET_KEY"] = app.config["JWT_SECRET_KEY"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=app.config["JWT_REFRESH_TOKEN_EXPIRES"])
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True 
    
    jwt = JWTManager(app)
    
    # Create custom error handlers for JWT
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return redirect(url_for('login'))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return redirect(url_for('login'))
        
    # Add a global authentication check for all routes
    @app.before_request
    def check_auth():
        # Skip authentication for these routes
        exempt_routes = [
            'login',           # Login page
            'logout',          # Logout page
            'static',          # Static files
            'favicon_ico'      # Favicon
        ]
        
        # Check if the current route is exempt
        if request.endpoint in exempt_routes:
            return  # Skip authentication check
            
        # Try to verify JWT token
        from flask_jwt_extended import verify_jwt_in_request
        try:
            verify_jwt_in_request(locations=["cookies"])
        except Exception:
            # If JWT verification fails, redirect to login
            return redirect(url_for('login'))
    
    # Add favicon routes
    @app.route('/favicon.ico')
    def favicon_ico():
        return send_from_directory(
            Path(app.root_path) / 'static' / 'images',
            'favicon.svg',
            mimetype='image/svg+xml'
        )


    @app.template_filter('to_nice_json')
    def to_nice_json(value):
        return json.dumps(value, indent=4)

    # Import and initialize routes
    from .routes.index import init_app as init_index_routes
    from .routes.home import init_app as init_home_routes
    from .routes.login import init_app as init_login_routes
    from .routes.pipelines import init_app as init_pipelines_routes
    from .routes.pipeline import init_app as init_pipeline_routes
    from .routes.import_pipeline import init_app as init_import_pipeline_routes
    from .routes.configs import init_app as init_import_configs_routes
    from .routes.run_configs import init_app as init_run_configs_routes
    from .routes.run_config import init_app as init_run_config_routes
    from .routes.storage import init_app as init_storage_routes
    from .routes.api.storage_backends import init_app as init_api__storage_backends
    from .routes.api.storage_list import init_app as init_api__storage_list
    from .routes.api.storage_download import init_app as init_api__storage_download
    from .routes.api.cache import init_app as init_api__cache
    from .routes.api.create_run_config import init_app as init_api__create_run_config

    # Create required directories
    root_dir = Path(app.config['ROOT_DIR'])
    root_dir.mkdir(parents=True, exist_ok=True)
    
    # Create pipeline and run_configs directories
    (root_dir / 'pipelines').mkdir(exist_ok=True)
    (root_dir / 'run_configs').mkdir(exist_ok=True)
    (root_dir / 'configs').mkdir(exist_ok=True)
    config_manager = ConfigManager(app, at_app_creation = True)

    # Initialize routes
    init_index_routes(app)
    init_home_routes(app)
    init_login_routes(app)
    init_pipelines_routes(app)
    init_pipeline_routes(app)
    init_import_pipeline_routes(app)
    init_import_configs_routes(app)
    init_run_configs_routes(app)
    init_run_config_routes(app)
    init_storage_routes(app)
    init_api__storage_backends(app)
    init_api__storage_list(app)
    init_api__storage_download(app)
    init_api__cache(app)
    init_api__create_run_config(app)

    return app
