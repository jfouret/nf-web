from flask import render_template, request, redirect, url_for, session
import os

def init_app(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            MASTER_PASSWORD = app.config['MASTER_PASSWORD']
            password_entered = request.form['password']
            if password_entered == MASTER_PASSWORD:
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error="Invalid password.")
        return render_template('login.html')
