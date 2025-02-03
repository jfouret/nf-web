from flask import Flask
import os
from dotenv import load_dotenv
from .config import Config
from .models import db, Pipeline
from .utils.cache import init_cache
import json

def create_app():
    app = Flask('nfui')
    load_dotenv()
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
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
    from .routes.api.checkout import init_app as init_api__checkout
    from .routes.run_configs import init_app as init_run_configs_routes
    from .routes.run_config import init_app as init_run_config_routes
    from .routes.api.create_run_config import init_app as init_api__create_run_config
    from .routes.storage import init_app as init_storage_routes
    from .routes.api.storage_backends import init_app as init_api__storage_backends
    from .routes.api.storage_list import init_app as init_api__storage_list
    from .routes.api.storage_download import init_app as init_api__storage_download
    from .routes.api.cache import init_app as init_api__cache

    root_dir = app.config['ROOT_DIR']
    pipelines_path = os.path.join(root_dir, 'pipelines')
    run_configs_path = os.path.join(root_dir, 'run_configs')
    configs_path = os.path.join(root_dir, 'configs')

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if not os.path.exists(root_dir):
        os.makedirs(run_configs_path)
    if not os.path.exists(pipelines_path):
        os.makedirs(pipelines_path)
    if not os.path.exists(configs_path):
        os.makedirs(configs_path)

    init_index_routes(app)
    init_home_routes(app)
    init_login_routes(app)
    init_pipelines_routes(app)
    init_pipeline_routes(app)
    init_import_pipeline_routes(app)
    init_import_configs_routes(app)
    init_run_configs_routes(app)
    init_run_config_routes(app)
    init_api__create_run_config(app)
    init_api__checkout(app)
    init_storage_routes(app)
    init_api__storage_backends(app)
    init_api__storage_list(app)
    init_api__storage_download(app)
    init_api__cache(app)

    return app
