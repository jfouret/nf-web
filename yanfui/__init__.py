from flask import Flask
import os
from dotenv import load_dotenv

def create_app():
    app = Flask('yanfui')  # Now explicitly using the name
    load_dotenv()
    app.secret_key = os.getenv('SECRET_KEY')

    # Import and initialize routes
    from .routes.index import init_app as init_index_routes
    from .routes.home import init_app as init_home_routes
    from .routes.login import init_app as init_login_routes

    init_index_routes(app)
    init_home_routes(app)
    init_login_routes(app)

    return app