from flask import redirect, url_for, session, request, flash
from ...utils.git import checkout_git
import os
import json

def init_app(app):
  @app.route('/api/checkout', methods=['POST'])  
  def init_api__checkout():
    if not session.get('logged_in'):
      return redirect(url_for('login'))
    if request.method == 'POST':
      data = request.get_json()
      root_dir = app.config['ROOT_DIR']
      pipelines_path = os.path.join(root_dir, 'pipelines')
      value = data["value"]  
      try:
        checkout_git(value, data["organization"], data["project"], data["rtype"],pipelines_path)
      except Exception as e:
        print(f'Error during checkout: {e}')
        flash(f'Error during checkout: {e}')
      return '', 200

