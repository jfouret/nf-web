import os
import string
import secrets
import time

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    ROOT_DIR = os.getenv('ROOT_DIR', 'root_dir')
    if ROOT_DIR.startswith('~'):
        ROOT_DIR = os.path.expanduser(ROOT_DIR)
    elif not ROOT_DIR.startswith('/'):
        ROOT_DIR = os.path.join(os.getcwd(), ROOT_DIR)
    # make sure the root dir exists
    os.makedirs(ROOT_DIR, exist_ok=True)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(ROOT_DIR, "nfui.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # GitHub configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # Token must be provided by user
    
    # Cache configuration
    CACHE_TYPE = "FileSystemCache"  # Use filesystem cache
    CACHE_DIR = os.path.join(ROOT_DIR, "cache")
    CACHE_DEFAULT_TIMEOUT = 3600  # Cache timeout in seconds
    CACHE_THRESHOLD = 1000  # Maximum number of items in the cache
    
    MASTER_PASSWORD = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(10))
    print(f'Password: {MASTER_PASSWORD}')
    print(f'GitHub Token: {GITHUB_TOKEN}')
