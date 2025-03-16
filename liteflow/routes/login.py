from flask import render_template, request, redirect, url_for, session, make_response, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
import bcrypt

def init_app(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            password_hash = app.config['PASSWORD_HASH'].encode('utf-8')
            password_entered = request.form['password'].encode('utf-8')
            if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                app.logger.error('Invalid POST request to /import_pipeline. Missing X-Requested-With=XMLHttpRequest header.')
                return jsonify({'error': 'Invalid request'}), 400
            
            if bcrypt.checkpw(password_entered, password_hash):
                access_token = create_access_token(identity="user")
                refresh_token = create_refresh_token(identity="user")
                response = jsonify({
                    'success': True,
                    'redirect': url_for('home')
                })
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)                
                return response
            else:
                return jsonify({
                    'success': False,
                    'error': "Invalid password."
                }), 401
        
        return render_template('login.html')
        
    @app.route('/logout', methods=['GET'])
    def logout():
        response = make_response(redirect(url_for('login')))
        unset_jwt_cookies(response)
        return response
