from flask import render_template, request, redirect, url_for, session, make_response, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from ..config import Config
from flask_jwt_extended import jwt_required

def init_app(app):
  @app.route('/login', methods=['GET', 'POST'])
  def login():
    if request.method == 'POST':
      password_hash = app.config['PASSWORD_HASH']
      password_entered = request.form['password']
      
      if Config.verify_password(password_entered, password_hash):
        # Create the tokens - identity is required by JWT but we only have one user
        # We use a simple string as identity since we don't need to store user-specific data
        access_token = create_access_token(identity="user")
        refresh_token = create_refresh_token(identity="user")
        
        # Check if this is an AJAX request or a regular form submission
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
          # For AJAX requests, return JSON
          response = jsonify({
            'success': True,
            'redirect': url_for('home')
          })
        else:
          # For regular form submissions, redirect
          response = make_response(redirect(url_for('home')))
        
        # Set the JWT cookies in the response
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)        
        return response
      else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
          return jsonify({
            'success': False,
            'error': "Invalid password."
          }), 401
        else:
          return render_template('login.html', error="Invalid password.")
    
    return render_template('login.html')
    
  @app.route('/logout', methods=['GET'])
  def logout():
    # Clear the JWT cookies
    response = make_response(redirect(url_for('login')))
    unset_jwt_cookies(response)
    
    # Clear the session for backward compatibility
    session.pop('logged_in', None)
    
    return response
