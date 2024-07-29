from flask import Flask
import os
from dotenv import load_dotenv
from .config import Config

def create_app():
    app = Flask('yanfui')  # Now explicitly using the name
    load_dotenv()
    app.config.from_object(Config)

    # Import and initialize routes
    from .routes.index import init_app as init_index_routes
    from .routes.home import init_app as init_home_routes
    from .routes.login import init_app as init_login_routes
    from .routes.pipelines import init_app as init_pipelines_routes
    from .routes.import_pipeline import init_app as init_import_pipeline_routes
    from .routes.configs import init_app as init_import_configs_routes
    from .routes.api.checkout import init_app as init_api__checkout

    root_dir = app.config['ROOT_DIR']
    pipelines_path = os.path.join(root_dir, 'pipelines')
    configs_path = os.path.join(root_dir, 'configs')

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if not os.path.exists(pipelines_path):
        os.makedirs(pipelines_path)
    if not os.path.exists(configs_path):
        os.makedirs(configs_path)

    init_index_routes(app)
    init_home_routes(app)
    init_login_routes(app)
    init_pipelines_routes(app)
    init_import_pipeline_routes(app)
    init_import_configs_routes(app)
    init_api__checkout(app)

    return app