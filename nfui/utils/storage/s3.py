import boto3
from datetime import datetime
from typing import Dict, List
from .base import BaseFile

class S3File(BaseFile):
    def __init__(self, settings: Dict):
        super().__init__(settings)
        self.s3 = boto3.client('s3', region_name=settings['region'])
        self.name = settings.get('name', '')
        # Convert string patterns to regex objects
        import re
        self.bucket_patterns = [re.compile(pattern) for pattern in settings['bucket_patterns']]

    def get_uri(self, path: str) -> str:
        return f"s3://{path}"

    def list(self, path: str = "") -> List[Dict]:
        items = []
        
        if not path:  # List buckets
            buckets = self.s3.list_buckets()['Buckets']
            for bucket in buckets:
                if any(pattern.match(bucket['Name']) for pattern in self.bucket_patterns):
                    items.append({
                        "name": bucket['Name'],
                        "uri": self.get_uri(bucket['Name']),
                        "type": "directory",
                        "created": bucket['CreationDate'],
                        "modified": bucket['CreationDate'],
                        "size": None
                    })
        else:  # List objects in bucket
            bucket, prefix = self._parse_path(path)
            if prefix != "" and not prefix.endswith("/"): 
                prefix = f"{prefix}/"
            paginator = self.s3.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter='/'):
                # Add directories
                for prefix in page.get('CommonPrefixes', []):
                    name = prefix['Prefix'].rstrip('/').split('/')[-1]
                    items.append({
                        "name": name,
                        "uri": self.get_uri(f"{bucket}/{prefix['Prefix']}"),
                        "type": "directory",
                        "created": None,
                        "modified": None,
                        "size": None
                    })
                
                # Add files
                for obj in page.get('Contents', []):
                    name = obj['Key'].split('/')[-1]
                    items.append({
                        "name": name,
                        "uri": self.get_uri(f"{bucket}/{obj['Key']}"),
                        "type": "file",
                        "created": None,
                        "modified": obj['LastModified'],
                        "size": obj['Size']
                    })
                    
        return items

    def get_download_url(self, path: str) -> str:
        try:
            bucket, key = self._parse_path(path)
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=3600
            )
            return url
        except Exception as e:
            return f"/api/storage/download?storage={self.name}&path={path}"

    def get_metadata(self, path: str) -> Dict:
        bucket, key = self._parse_path(path)
        obj = self.s3.head_object(Bucket=bucket, Key=key)
        return {
            "created": None,
            "modified": obj['LastModified'],
            "size": obj['ContentLength']
        }

    def _parse_path(self, path: str) -> tuple[str, str]:
        """Split path into bucket and key"""
        parts = path.split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        return bucket, key
