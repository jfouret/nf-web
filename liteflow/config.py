import os
import string
import secrets
import time
import bcrypt
import yaml
import json
import jsonschema
from pathlib import Path
"""_summary_

Configuration with environment variables for LiteFlow.

Configs variable starts with LITEFLOW_

Documentation:

LITEFLOW_ROOT_DIR: The root directory for LiteFlow. Default is 'root_dir'.
LITEFLOW_LOGIN_PASSWORD_HASH: The hashed password for logging in to LiteFlow.
    Default is a random string.
LITEFLOW_LOGIN_PASSWORD: The password for logging in to LiteFlow. Default is a
    random string.
LITEFLOW_SECRET_KEY: The secret key for LiteFlow. Default is a random string.
LITEFLOW_GITHUB_TOKEN: The GitHub token for LiteFlow. Default is an empty
    string.
LITEFLOW_SQLALCHEMY_DATABASE_URI: The database URI for LiteFlow. Default is
    'sqlite:/{root_dir}/liteflow.db'.
LITEFLOW_STORAGE_CONFIG: Path to a YAML file containing storage backend
    configurations. If not provided, default storage backends will be used.
    The YAML file can use {{ROOT_DIR}} as a placeholder for the LiteFlow root
    directory.
JWT_SECRET_KEY: The secret key for JWT. Default is the same as
    LITEFLOW_SECRET_KEY.
JWT_ACCESS_TOKEN_EXPIRES: The expiration time for JWT access tokens.
    Default is 3600 seconds (1 hour).
JWT_REFRESH_TOKEN_EXPIRES: The expiration time for JWT refresh tokens.
    Default is 2592000 seconds (30 days).

"""

class Config:

    # Load from environment variables
    SECRET_KEY = os.getenv('LITEFLOW_SECRET_KEY', 'default_secret_key')
    ROOT_DIR = Path(
        os.getenv('LITEFLOW_ROOT_DIR', 'liteflow_root_dir')
    ).resolve()
    PASSWORD_HASH = os.getenv('LITEFLOW_LOGIN_PASSWORD_HASH', None)
    if not PASSWORD_HASH: password = os.getenv('LITEFLOW_LOGIN_PASSWORD', None)
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "LITEFLOW_SQLALCHEMY_DATABASE_URI",
        f'sqlite:///{str(ROOT_DIR)}/liteflow.db'
    )
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)
    )
    JWT_REFRESH_TOKEN_EXPIRES = int(
        os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)
    )
    STORAGE_BACKEND_CONFIG = Path(os.getenv(
        "LITEFLOW_STORAGE_CONFIG",
        Path(__file__).parent / 'assets' / 'storage_backends.yaml'
    ))
    
    # make sure the root dir exists
    ROOT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cache configuration
    CACHE_TYPE = "FileSystemCache"  # Use filesystem cache
    CACHE_DIR = ROOT_DIR / "cache"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DEFAULT_TIMEOUT = 3600  # Cache timeout in seconds
    CACHE_THRESHOLD = 1000  # Maximum number of items in the cache

    DATA_DIR = ROOT_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    CONFIGS_DIR = ROOT_DIR / "configs"
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

    PIPELINES_DIR = ROOT_DIR / "pipelines"
    PIPELINES_DIR.mkdir(parents=True, exist_ok=True)

    RUN_CONFIG_DIR = ROOT_DIR / "run_configs"
    RUN_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    RUN_DIR = ROOT_DIR / "runs"
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_storage_backends(config_path, root_dir):
        """
        Load storage backends from YAML file and validate against schema.
        
        Args:
            config_path: Path to the YAML configuration file.
            root_dir: Root directory to replace {{ROOT_DIR}} placeholder.
            
        Returns:
            dict: Storage backends configuration
        """
            
        # Schema path
        schema_path = Path(__file__).parent / 'assets' / 'storage_backends_schema.json'
        
        # Load schema
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        # Load config
        storage_backends = yaml.safe_load(Path(config_path).read_text())
        
        # Replace {{ROOT_DIR}} placeholder with actual path in all backends
        for backend_name, backend_config in storage_backends.items():
            if 'root' in backend_config:
                backend_config['root'] = backend_config['root'].replace(
                    "{{ROOT_DIR}}", str(root_dir)
                )
                
        # Validate config against schema
        jsonschema.validate(instance=storage_backends, schema=schema)
        
        return storage_backends

    
    # Password handling with bcrypt
    if PASSWORD_HASH:
        if not PASSWORD_HASH.startswith('$2b$'):
            raise ValueError(
                "LITEFLOW_PASSWORD_HASH must be a valid bcrypt hash starting "
                "with $2b$"
            )
    else:
        if not password:
            raise ValueError(
                "Either LITEFLOW_LOGIN_PASSWORD_HASH or "
                "LITEFLOW_LOGIN_PASSWORD must be set in the environment "
                "variables."
            )
        PASSWORD_HASH = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        del password
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        """Verify a password against a hash using bcrypt"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
