from flask import render_template, request, redirect, url_for, session, flash
from pathlib import Path
from ..utils.workflow.config import ConfigManager

def init_app(app):
    config_manager = ConfigManager(app, at_app_creation=False)

    @app.route('/configs', methods=['GET', 'POST'])
    def configs():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            try:
                config = config_manager.create_config(
                    name=request.form['name'],
                    filename=request.form['filename']
                )
                return redirect(url_for('edit_config', filename=config['filename']))
            except ValueError as e:
                flash(str(e), category='error')
                return redirect(url_for('configs'))

        configs = config_manager.list_configs()
        default_config = config_manager.get_default()
        return render_template('configs.html', 
                             config_files=configs,
                             default_config=default_config,
                             can_change_default=not config_manager.has_enforced_default)

    @app.route('/configs/set_default/<filename>', methods=['POST'])
    def set_default_config(filename):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        if config_manager.has_enforced_default:
            flash('Default config is enforced by system configuration!', category='error')
            return redirect(url_for('configs'))
        
        try:
            config_manager.set_default(filename)
            flash('Default configuration updated!', category='success')
        except FileNotFoundError:
            flash('Configuration not found!', category='error')
        
        return redirect(url_for('configs'))

    @app.route('/configs/edit/<filename>', methods=['GET', 'POST'])
    def edit_config(filename):
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        try:
            config = config_manager.get_config(filename)
            
            if request.method == 'POST':
                config_manager.update_config(filename, request.form['content'])
                flash('Configuration saved!', category='success')
                return redirect(url_for('configs'))

            # Get config file content
            with config_manager.get_config_path(filename).open('r') as f:
                content = f.read()
                
            return render_template('edit_config.html', filename=filename, content=content)
            
        except FileNotFoundError:
            flash('Configuration not found!', category='error')
            return redirect(url_for('configs'))

    @app.route('/configs/delete/<filename>', methods=['POST'])
    def delete_config(filename):
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        try:
            # Get config first to check if it's default
            config = config_manager.get_config(filename)
            if config['is_default']:
                flash('Cannot delete the default configuration!', category='error')
                return redirect(url_for('configs'))
            
            config_manager.delete_config(filename)
            flash('Configuration deleted!', category='success')
            
        except FileNotFoundError:
            flash('Configuration not found!', category='error')
        except ValueError as e:
            flash(str(e), category='error')
            
        return redirect(url_for('configs'))
