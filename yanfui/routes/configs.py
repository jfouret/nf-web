from flask import render_template, request, redirect, url_for, session, flash
from ..utils.file_utils import list_config_files, save_config_file, delete_config_file, read_config_file
import os
import yaml

def init_app(app):
    @app.route('/configs', methods=['GET', 'POST'])
    def configs():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        root_dir = app.config['ROOT_DIR']
        configs_path = os.path.join(root_dir, 'configs')
        if request.method == 'POST':
            name = request.form['name']
            filename = request.form['filename']
            if not filename.endswith('.config'):
                filename += '.config'
            filepath = os.path.join(configs_path, filename)
            meta_filepath = f'{filepath}.meta.yml'
            with open(meta_filepath, 'w') as meta_file:
                yaml.dump({'name': name, 'filename': filename}, meta_file)
            with open(filepath, 'w') as file:
                file.write('')
            return redirect(url_for('edit_config', filename=filename))

        config_files = list_config_files(configs_path)
        return render_template('configs.html', config_files=config_files)

    @app.route('/configs/edit/<filename>', methods=['GET', 'POST'])
    def edit_config(filename):
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        root_dir = app.config['ROOT_DIR']
        filepath = os.path.join(root_dir, 'configs', filename)
        if request.method == 'POST':
            content = request.form['content']
            save_config_file(filepath, content)
            flash('Configuration saved!', category='success')
            return redirect(url_for('configs'))

        content = read_config_file(filepath)
        return render_template('edit_config.html', filename=filename, content=content)

    @app.route('/configs/delete/<filename>', methods=['POST'])
    def delete_config(filename):
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        root_dir = app.config['ROOT_DIR']
        filepath = os.path.join(root_dir, 'configs', filename)
        delete_config_file(filepath)
        flash('Configuration deleted!', category='success')
        return redirect(url_for('configs'))
