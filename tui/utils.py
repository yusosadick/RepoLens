"""TUI utilities for RepoLens - ASCII art, formatting, and helper functions."""

import os
import re
import getpass
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.text import Text

from utils import normalize_path

# TODO: Consider caching banner generation for performance
# TODO: Add support for custom banner styles/configurations
# TODO: Implement terminal width detection for responsive banner sizing

REPOLENS_BANNER = """ ____  _____ ____       _     _____ _   _ ____  
|  _ \\| ____|  _ \\ ___ | |   | ____| \\ | / ___| 
| |_) |  _| | |_) / _ \\| |   |  _| |  \\| \\___ \\ 
|  _ <| |___|  __/ (_) | |___| |___| |\\  |___) |
|_| \\_\\_____|_|   \\___/|_____|_____|_| \\_|____/"""


def get_username() -> str:
    """
    Get system username.
    
    Returns:
        Username string
    """
    # TODO: Add fallback for Windows username detection
    # TODO: Consider using pwd module for more reliable username retrieval
    return os.getenv("USER") or os.getenv("USERNAME") or getpass.getuser()


def generate_header() -> str:
    """
    Generate RepoLens ASCII header banner with exact format.
    
    Returns:
        Complete header string with banner, subtitle, user info, and footer
    """
    # TODO: Optimize header generation for faster rendering
    # TODO: Add color support based on terminal capabilities
    # TODO: Implement header caching to avoid regeneration
    username = get_username()
    
    header_lines = [
        REPOLENS_BANNER,
        "",
        "🔍 RepoLens — Repository Intelligence Engine",
        f"User: {username}",
        "Mode: Interactive",
        "",
        "💻 currently working on web & mobile apps and backend systems.",
        "",
        "   I love coding, lets connect  instagram.com/yuso_sadick/",
        "",
        "      ☕ Buy me a coffee  buymeacoffee.com/yuso_sadick",
    ]
    
    return "\n".join(header_lines)


def format_menu_item(number: str, text: str, selected: bool = False) -> str:
    """
    Format a menu item with consistent styling.
    
    Args:
        number: Menu number (e.g., "01", "02", "00")
        text: Menu item text
        selected: Whether this item is currently selected
        
    Returns:
        Formatted menu item string
    """
    # TODO: Add keyboard navigation highlighting
    # TODO: Implement color themes for menu items
    # TODO: Add support for disabled menu items
    prefix = "> " if selected else "  "
    return f"{prefix}{number}. {text}"


def validate_directory_path(path: str) -> tuple[bool, Optional[str]]:
    """
    Validate a directory path with full path resolution.
    
    Args:
        path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        Error messages: "Directory not found", "Path is not a directory", "Permission denied"
    """
    try:
        normalized = normalize_path(path)
        
        if not normalized.exists():
            return False, "Directory not found"
        
        if not normalized.is_dir():
            return False, "Path is not a directory"
        
        # Check read permissions
        if not os.access(normalized, os.R_OK):
            return False, "Permission denied"
        
        return True, None
    except Exception as e:
        return False, f"Invalid path: {str(e)}"


def is_git_repository(path: str) -> bool:
    """
    Check if a directory is a valid Git repository.
    
    Args:
        path: Path to directory to check
        
    Returns:
        True if directory contains a valid .git folder or file
    """
    try:
        normalized = normalize_path(path)
        git_path = normalized / ".git"
        return git_path.exists() and (git_path.is_dir() or git_path.is_file())
    except Exception:
        return False


def validate_git_repository(path: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a path is a Git repository.
    
    Args:
        path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        Error message: "Git repository not found" if not a Git repo
    """
    is_valid, error = validate_directory_path(path)
    if not is_valid:
        return False, error
    
    if not is_git_repository(path):
        return False, "Git repository not found"
    
    return True, None


def validate_github_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate a GitHub repository URL with support for multiple formats.
    
    Supported formats:
    - HTTPS: https://github.com/user/repo
    - HTTPS with .git: https://github.com/user/repo.git
    - SSH: git@github.com:user/repo.git
    - With trailing slash: https://github.com/user/repo/
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        Error messages: "Invalid GitHub URL", "GitHub repository not accessible"
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"
    
    url = url.strip()
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    # HTTPS URL pattern (supports http/https, www optional, .git optional)
    https_pattern = r'^https?://(www\.)?github\.com/[\w\-\.]+/[\w\-\.]+(\.git)?$'
    
    # SSH URL pattern (git@github.com:user/repo.git)
    ssh_pattern = r'^git@github\.com:[\w\-\.]+/[\w\-\.]+(\.git)?$'
    
    if re.match(https_pattern, url) or re.match(ssh_pattern, url):
        return True, None
    
    return False, "Invalid GitHub URL. Expected format: https://github.com/user/repo or git@github.com:user/repo.git"


def open_file_manager(path: str) -> None:
    """
    Open file manager at given path (platform-specific).
    
    Args:
        path: Path to open in file manager
    """
    # TODO: Add error handling for file manager launch failures
    # TODO: Support alternative file managers on Linux
    # TODO: Add logging for debugging file manager operations
    import platform
    import subprocess
    
    system = platform.system()
    
    try:
        if system == "Linux":
            subprocess.run(["xdg-open", path], check=False)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", path], check=False)
        elif system == "Windows":
            subprocess.run(["explorer", path], check=False)
        else:
            # TODO: Add support for other platforms
            pass
    except Exception:
        # TODO: Implement proper error reporting for file manager failures
        pass
