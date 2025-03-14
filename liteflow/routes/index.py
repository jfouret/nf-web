from flask import redirect, url_for, session
from flask_jwt_extended import jwt_required

def init_app(app):
    @app.route('/')
    def index():
        return redirect(url_for('home'))