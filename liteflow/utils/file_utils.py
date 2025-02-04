import hashlib
from pathlib import Path

def get_file_digest(filepath: Path):
    """Calculate SHA256 digest of a file"""
    sha256_hash = hashlib.sha256()
    with filepath.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
