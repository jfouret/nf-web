from flask import redirect, url_for, session

def init_app(app):
  @app.route('/')
  def index():
    if not session.get('logged_in'):
      return redirect(url_for('login'))
    else:
      return redirect(url_for('home'))