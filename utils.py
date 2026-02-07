"""Utility functions, configuration constants, and internationalization support for RepoLens."""

import os
import re
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Set, Dict

# ============================================================================
# Configuration Constants
# ============================================================================

# Directories to skip during analysis
SKIP_DIRECTORIES: Set[str] = {".git", "node_modules", "build", "dist", "__pycache__", ".pytest_cache"}

# Common binary file extensions
BINARY_EXTENSIONS: Set[str] = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".a", ".lib",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".svg",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".db", ".sqlite", ".sqlite3",
}

# Default language
DEFAULT_LANGUAGE: str = "en"

# Binary detection chunk size (bytes to read for null byte detection)
BINARY_DETECTION_CHUNK_SIZE: int = 8192

# ============================================================================
# Path Utilities
# ============================================================================


def normalize_path(path: str) -> Path:
    """
    Normalize and resolve a path string to absolute Path object.
    
    Handles:
    - Tilde expansion (~/path, ~user/path)
    - Relative paths (./path, ../path)
    - Symlinks (resolves to actual path)
    - Paths with spaces
    
    Args:
        path: Path string to normalize
        
    Returns:
        Resolved absolute Path object
    """
    # Expand tilde to home directory
    expanded = os.path.expanduser(path)
    # Resolve to absolute path (handles relative paths and symlinks)
    return Path(expanded).resolve()


# ============================================================================
# GitHub Repository Utilities
# ============================================================================


def extract_repo_name(path_or_url: str) -> str:
    """
    Extract repository name from GitHub URL or local path.
    
    Args:
        path_or_url: GitHub repository URL or local directory path
        
    Returns:
        Sanitized repository name, or "unknown" if extraction fails
    """
    if not path_or_url:
        return "unknown"
    
    # Handle GitHub URLs
    github_pattern = r'github\.com[/:]([\w\-\.]+)/([\w\-\.]+)'
    match = re.search(github_pattern, path_or_url)
    if match:
        repo_name = match.group(2)  # Get the repo name (second group)
        # Remove .git suffix if present (use endswith to avoid rstrip issues)
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        return _sanitize_filename(repo_name)
    
    # Handle local paths
    try:
        path_obj = Path(path_or_url)
        # Get the directory name
        if path_obj.is_dir():
            repo_name = path_obj.name
        else:
            # If it's a file, get parent directory name
            repo_name = path_obj.parent.name
        
        # If the name is empty or just ".", try to get from absolute path
        if not repo_name or repo_name == ".":
            repo_name = path_obj.resolve().name
        
        return _sanitize_filename(repo_name) if repo_name else "unknown"
    except Exception:
        return "unknown"


def _sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.
    
    Args:
        name: String to sanitize
        
    Returns:
        Sanitized string safe for filenames
    """
    if not name:
        return "unknown"
    
    # Remove invalid filename characters
    # Windows: < > : " / \ | ? *
    # Unix: / (forward slash)
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '_', name)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length to reasonable size
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    # If empty after sanitization, return unknown
    return sanitized if sanitized else "unknown"


def clone_repository(repo_url: str) -> str:
    """
    Clone a GitHub repository to a temporary directory.
    
    Supports both HTTPS and SSH URLs:
    - HTTPS: https://github.com/user/repo or https://github.com/user/repo.git
    - SSH: git@github.com:user/repo.git
    
    Args:
        repo_url: GitHub repository URL (HTTPS or SSH format)
        
    Returns:
        Path to the cloned repository directory
        
    Raises:
        RuntimeError: If cloning fails with specific error message
    """
    # Check if Git is available before attempting clone
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        raise RuntimeError("Git is not installed or not in PATH. Please install Git to clone repositories.")
    
    # Normalize URL (remove trailing slash if present)
    repo_url = repo_url.strip().rstrip('/')
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="repolens_")
    
    try:
        # Clone the repository (works with both HTTPS and SSH URLs)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minute timeout
        )
        return temp_dir
    except subprocess.CalledProcessError as e:
        # Cleanup on failure
        cleanup_temp_directory(temp_dir)
        error_msg = e.stderr.strip() if e.stderr else "Unknown error"
        # Provide more specific error messages
        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise RuntimeError(f"GitHub repository not found: {repo_url}")
        elif "permission denied" in error_msg.lower() or "authentication" in error_msg.lower():
            raise RuntimeError(f"Permission denied. Check your Git authentication for: {repo_url}")
        else:
            raise RuntimeError(f"Failed to clone repository: {error_msg}")
    except subprocess.TimeoutExpired:
        # Cleanup on timeout
        cleanup_temp_directory(temp_dir)
        raise RuntimeError("Repository clone timed out after 5 minutes")


def cleanup_temp_directory(path: str) -> None:
    """
    Remove a temporary directory and all its contents.
    
    Args:
        path: Path to the directory to remove
    """
    try:
        path_obj = Path(path)
        if path_obj.exists() and path_obj.is_dir():
            shutil.rmtree(path)
    except (OSError, PermissionError):
        # Ignore cleanup errors - the OS will handle it eventually
        pass


# ============================================================================
# Internationalization Support
# ============================================================================

# Cache for loaded languages
_language_cache: Dict[str, Dict[str, str]] = {}


def get_language_file_path(lang: str) -> Path:
    """
    Get the path to a language file.
    
    Args:
        lang: Language code (e.g., "en", "es", "ar")
        
    Returns:
        Path to the language JSON file
    """
    # Get the directory where this module is located
    module_dir = Path(__file__).parent
    return module_dir / "languages" / f"{lang}.json"


def load_language(lang: str) -> Dict[str, str]:
    """
    Load a language file and cache it.
    
    Args:
        lang: Language code (e.g., "en", "es", "ar")
        
    Returns:
        Dictionary of translations for the language
    """
    # Return from cache if available
    if lang in _language_cache:
        return _language_cache[lang]
    
    lang_path = get_language_file_path(lang)
    
    try:
        with open(lang_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
            _language_cache[lang] = translations
            return translations
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to English if language file doesn't exist
        if lang != DEFAULT_LANGUAGE:
            return load_language(DEFAULT_LANGUAGE)
        # If English is missing, return empty dict
        return {}


def get_text(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Get translated text for a key, with fallback to English.
    
    Args:
        key: Translation key
        lang: Language code (default: English)
        
    Returns:
        Translated text, or the key itself if not found
    """
    translations = load_language(lang)
    
    # Try requested language first
    if key in translations:
        return translations[key]
    
    # Fallback to English if not the requested language
    if lang != DEFAULT_LANGUAGE:
        en_translations = load_language(DEFAULT_LANGUAGE)
        if key in en_translations:
            return en_translations[key]
    
    # If still not found, return the key
    return key
