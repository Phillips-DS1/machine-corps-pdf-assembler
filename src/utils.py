# Filename: src/utils.py
import os
import re
from hashlib import sha256
from pathlib import Path

def discover_files(input_folder: str) -> list[Path]:
    """Discover and sort Markdown files by numeric prefix (e.g., 01-, 10-)."""
    folder = Path(input_folder)
    if not folder.is_dir():
        raise ValueError(f"Input folder does not exist: {input_folder}")
    
    md_files = [f for f in folder.iterdir() if f.suffix.lower() == '.md' and f.is_file()]
    md_files.sort(key=lambda f: (get_file_order(f.name), f.name))
    return md_files

def get_file_order(filename: str) -> tuple[int, str]:
    """Extract numeric prefix for sorting (handles 1- to 999- gracefully)."""
    match = re.match(r'(\d+)-', filename)
    if match:
        return int(match.group(1)), filename
    return 999, filename

def compute_hash(file_path: str | Path) -> str:
    """Compute SHA-256 hash of a file for deterministic verification."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found for hashing: {file_path}")
    with open(path, 'rb') as f:
        return sha256(f.read()).hexdigest()

def ensure_directory(path: str | Path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)