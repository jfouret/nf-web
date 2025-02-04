# Storage System Documentation

## Overview
The storage system provides a read-only interface for browsing and downloading files from various storage backends. It supports both local file system storage and AWS S3 storage, with a flexible architecture that allows for easy addition of new storage backends.

## Components

### 1. Base Classes
Located in `liteflow/utils/storage/base.py`, the `BaseFile` abstract class defines the interface that all storage backends must implement:
- `get_uri(path)`: Returns a full URI for a given path
- `list(path)`: Lists files and directories at the given path
- `get_download_url(path)`: Generates a download URL for a file
- `get_metadata(path)`: Retrieves file metadata

### 2. Storage Backends

#### Local File System Backend (`liteflow/utils/storage/server.py`)
The `ServerFile` class implements local file system storage:
- Uses Python's standard library for file operations
- Maps local paths to file:// URIs
- Provides direct file access through the web server

#### S3 Backend (`liteflow/utils/storage/s3.py`)
The `S3File` class implements AWS S3 storage:
- Uses boto3 for S3 operations
- Supports bucket listing and object browsing
- Generates pre-signed URLs for secure downloads
- Configurable bucket access patterns

### 3. Storage Manager
Located in `liteflow/utils/storage/manager.py`, the `StorageManager` class:
- Manages multiple storage backends
- Initializes backends based on configuration
- Provides a unified interface for accessing different storage types

### 4. API Routes

#### Backend Listing (`liteflow/routes/api/storage_backends.py`)
- `GET /api/storage/backends`: Lists available storage backends

#### File Operations (`liteflow/routes/api/storage_list.py`, `storage_download.py`)
- `GET /api/storage/<backend>/list`: Lists files in a directory
- `GET /api/storage/download`: Downloads a file

### 5. Web Interface
Located in `liteflow/templates/storage.html`, provides:
- Backend selection sidebar
- File/directory browser
- Path navigation breadcrumbs
- Download links for files

## Configuration
Storage backends are configured in `liteflow/config.py` under `STORAGE_BACKENDS`:
```python
STORAGE_BACKENDS = {
    'local_data': {
        'type': 'server',
        'root': os.path.join(ROOT_DIR, 'data'),
        'description': 'Local Data Files'
    },
    'local_configs': {
        'type': 'server',
        'root': os.path.join(ROOT_DIR, 'configs'),
        'description': 'Configuration Files'
    },
    'aws_data': {
        'type': 's3',
        'bucket_patterns': ['.*'],
        'region': "eu-west-3",
        'description': 'AWS Data Storage'
    }
}
```

## Security
- Read-only access to prevent unauthorized modifications
- Authentication required for all operations
- Path validation to prevent directory traversal
- S3 pre-signed URLs for secure, time-limited access

## Dependencies
- boto3: AWS SDK for S3 operations
- python-magic: For MIME type detection
