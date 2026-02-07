"""Core analysis engine for RepoLens."""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from utils import SKIP_DIRECTORIES, BINARY_EXTENSIONS, BINARY_DETECTION_CHUNK_SIZE, normalize_path


def is_binary_file(filepath: str) -> bool:
    """
    Detect if a file is binary.
    
    Checks for null bytes in the first chunk of the file,
    or checks against known binary extensions.
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        True if the file appears to be binary, False otherwise
    """
    path = Path(filepath)
    
    # Check extension first (faster)
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    
    # Check for null bytes
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(BINARY_DETECTION_CHUNK_SIZE)
            if b"\x00" in chunk:
                return True
    except (OSError, IOError):
        # If we can't read it, assume it's not a text file we can analyze
        return True
    
    return False


def get_file_extension(filepath: str) -> str:
    """
    Get the file extension or filename for special files without extensions.
    
    For files like Makefile, Dockerfile, LICENSE, etc., returns the filename
    itself to enable proper language detection.
    
    Args:
        filepath: Path to the file
        
    Returns:
        File extension (e.g., ".py") or filename for extensionless files
    """
    path = Path(filepath)
    ext = path.suffix.lower()
    
    if ext:
        return ext
    
    # For files without extension, return the filename for special file detection
    # This allows Makefile, Dockerfile, LICENSE, etc. to be properly categorized
    filename = path.name
    return filename if filename else ""


def analyze_file(filepath: str) -> Optional[Dict[str, int]]:
    """
    Analyze a single file and return its statistics.
    
    Args:
        filepath: Path to the file to analyze
        
    Returns:
        Dictionary with 'lines' and 'characters' keys, or None if file cannot be analyzed
    """
    if is_binary_file(filepath):
        return None
    
    try:
        lines = 0
        characters = 0
        
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                lines += 1
                characters += len(line)
        
        return {"lines": lines, "characters": characters}
    except (OSError, IOError, UnicodeDecodeError):
        # Skip files we can't read
        return None


def analyze_directory(path: str) -> Dict[str, Any]:
    """
    Analyze a directory recursively and return statistics.
    
    Args:
        path: Path to the directory to analyze (will be normalized)
        
    Returns:
        Dictionary with the following structure:
        {
            "total_files": int,
            "total_lines": int,
            "total_characters": int,
            "by_extension": {
                ".py": {
                    "files": int,
                    "lines": int,
                    "characters": int
                },
                ...
            }
        }
    """
    # Normalize path for consistent handling (handles tilde, relative paths, symlinks)
    try:
        path_obj = normalize_path(path)
    except Exception:
        # If normalization fails, try with Path directly
        path_obj = Path(path)
    
    if not path_obj.exists() or not path_obj.is_dir():
        return {
            "total_files": 0,
            "total_lines": 0,
            "total_characters": 0,
            "by_extension": {}
        }
    
    # Use string path for os.walk (works with both Path and str)
    path_str = str(path_obj)
    
    total_files = 0
    total_lines = 0
    total_characters = 0
    by_extension: Dict[str, Dict[str, int]] = {}
    
    # Walk directory recursively
    for root, dirs, files in os.walk(path_str):
        # Filter out skip directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRECTORIES]
        
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = get_file_extension(filepath)
            
            # Analyze the file
            stats = analyze_file(filepath)
            if stats is None:
                continue
            
            total_files += 1
            total_lines += stats["lines"]
            total_characters += stats["characters"]
            
            # Group by extension
            if ext not in by_extension:
                by_extension[ext] = {"files": 0, "lines": 0, "characters": 0}
            
            by_extension[ext]["files"] += 1
            by_extension[ext]["lines"] += stats["lines"]
            by_extension[ext]["characters"] += stats["characters"]
    
    return {
        "total_files": total_files,
        "total_lines": total_lines,
        "total_characters": total_characters,
        "by_extension": by_extension
    }
