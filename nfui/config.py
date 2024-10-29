import os
import string
import secrets

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    ROOT_DIR = os.getenv('ROOT_DIR', 'root_dir')
    if ROOT_DIR.startswith('~'):
        ROOT_DIR = os.path.expanduser(ROOT_DIR)
    elif not ROOT_DIR.startswith('/'):
        ROOT_DIR = os.path.join(os.getcwd(), ROOT_DIR)
    # make sure the root dir exists
    os.makedirs(ROOT_DIR, exist_ok=True)
    MASTER_PASSWORD = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(10))
    print(f'Password: {MASTER_PASSWORD}')