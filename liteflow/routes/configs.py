from flask import render_template, request, redirect, url_for, session, flash, jsonify
from pathlib import Path
from ..utils.workflow.config import ConfigManager

def init_app(app):
    config_manager = ConfigManager(app, at_app_creation=False)

    @app.route('/configs', methods=['GET', 'POST'])
    def configs():        
        if request.method == 'POST':
            if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                app.logger.error('Invalid POST request to /configs. Missing X-Requested-With=XMLHttpRequest header.')
                return jsonify({'error': 'Invalid request'}), 400
                
            try:
                config = config_manager.create_config(
                    name=request.form['name'],
                    filename=request.form['filename']
                )
                return jsonify({
                    'success': True, 
                    'message': f"Configuration for '{request.form['filename']}' created successfully!",
                    "config": config
                })
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        configs = config_manager.list_configs()
        default_config = config_manager.get_default()
        return render_template('configs.html', 
                             config_files=configs,
                             default_config=default_config,
                             can_change_default=not config_manager.has_enforced_default)

    @app.route('/configs/set_default/<filename>', methods=['POST'])
    def set_default_config(filename):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            app.logger.error('Invalid POST request to /configs/set_default. Missing X-Requested-With=XMLHttpRequest header.')
            return jsonify({'error': 'Invalid request'}), 400
        
        if config_manager.has_enforced_default:
            return jsonify({'error': 'Default config is enforced by system configuration!'}), 400
        
        try:
            config_manager.set_default(filename)
            return jsonify({'success': True, 'message': 'Default configuration updated!'})
        except FileNotFoundError:
            return jsonify({'error': 'Configuration not found!'}), 404

    @app.route('/configs/edit/<filename>', methods=['GET', 'POST'])
    def edit_config(filename):
        try:
            config = config_manager.get_config(filename)
            
            if request.method == 'POST':
                if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                    app.logger.error('Invalid POST request to /configs/edit. Missing X-Requested-With=XMLHttpRequest header.')
                    return jsonify({'error': 'Invalid request'}), 400
                
                config_manager.update_config(filename, request.form['content'])
                return jsonify({'success': True, 'message': 'Configuration saved!'})

            # GET request - render the template
            with config_manager.get_config_path(filename).open('r') as f:
                content = f.read()
                
            return render_template('edit_config.html', filename=filename, content=content)
            
        except FileNotFoundError:
            if request.method == 'POST':
                return jsonify({'error': 'Configuration not found!'}), 404
            
            flash('Configuration not found!', category='error')
            return redirect(url_for('configs'))

    @app.route('/configs/delete/<filename>', methods=['POST'])
    def delete_config(filename):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            app.logger.error('Invalid POST request to /configs/delete. Missing X-Requested-With=XMLHttpRequest header.')
            return jsonify({'error': 'Invalid request'}), 400

        try:
            # Get config first to check if it's default
            config = config_manager.get_config(filename)
            if config['is_default']:
                return jsonify({'error': 'Cannot delete the default configuration!'}), 400
            
            config_manager.delete_config(filename)
            return jsonify({'success': True, 'message': 'Configuration deleted!'})
            
        except FileNotFoundError:
            return jsonify({'error': 'Configuration not found!'}), 404
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
