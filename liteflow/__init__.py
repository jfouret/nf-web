from flask import Flask
from pathlib import Path
from .utils.workflow import ConfigManager
from dotenv import load_dotenv
from .config import Config
from . import models
from .utils.cache import init_cache
import json

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
