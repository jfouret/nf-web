from flask import render_template, redirect, url_for, session
from ..utils.system_info import get_system_info
from ..utils.software_info import get_software_versions
from flask_jwt_extended import jwt_required

def init_app(app):
  @app.route('/home')
  def home():
    info = get_system_info()
    software_versions = get_software_versions()
    return render_template('home.html', info=info, software_versions=software_versions)