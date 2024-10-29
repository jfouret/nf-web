import os
import yaml

def list_config_files(configs_path):
    config_files = []
    for filename in os.listdir(configs_path):
        if filename.endswith('.meta.yml'):
            with open(os.path.join(configs_path, filename), 'r') as file:
                meta = yaml.safe_load(file)
            config_files.append(meta)
    return config_files

def read_config_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

def save_config_file(filepath, content):
    with open(filepath, 'w') as file:
        file.write(content)

def delete_config_file(filepath):
    os.remove(filepath)
    meta_filepath = f'{filepath}.meta.yml'
    os.remove(meta_filepath)
