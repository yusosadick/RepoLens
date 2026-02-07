"""Tests for the analyzer module."""

import os
import tempfile
import pytest
from pathlib import Path

from analyzer import (
    analyze_directory,
    analyze_file,
    is_binary_file,
    get_file_extension
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    import shutil
    shutil.rmtree(temp_path, ignore_errors=True)


def test_get_file_extension():
    """Test file extension extraction."""
    assert get_file_extension("test.py") == ".py"
    assert get_file_extension("test.js") == ".js"
    assert get_file_extension("test") == ""
    assert get_file_extension("test.TXT") == ".txt"  # Lowercase
    assert get_file_extension("path/to/file.py") == ".py"


def test_is_binary_file_text():
    """Test binary detection for text files."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("print('hello')\nprint('world')")
        temp_path = f.name
    
    try:
        assert not is_binary_file(temp_path)
    finally:
        os.unlink(temp_path)


def test_is_binary_file_by_extension():
    """Test binary detection by extension."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"fake png data")
        temp_path = f.name
    
    try:
        assert is_binary_file(temp_path)
    finally:
        os.unlink(temp_path)


def test_analyze_file_text():
    """Test analyzing a text file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3")
        temp_path = f.name
    
    try:
        result = analyze_file(temp_path)
        assert result is not None
        assert result["lines"] == 3
        assert result["characters"] == len("Line 1\nLine 2\nLine 3")
    finally:
        os.unlink(temp_path)


def test_analyze_file_binary():
    """Test that binary files return None."""
    with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
        f.write(b"binary data\x00\x01\x02")
        temp_path = f.name
    
    try:
        result = analyze_file(temp_path)
        assert result is None
    finally:
        os.unlink(temp_path)


def test_analyze_directory_empty(temp_dir):
    """Test analyzing an empty directory."""
    result = analyze_directory(temp_dir)
    assert result["total_files"] == 0
    assert result["total_lines"] == 0
    assert result["total_characters"] == 0
    assert result["by_extension"] == {}


def test_analyze_directory_single_file(temp_dir):
    """Test analyzing a directory with a single file."""
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text("print('hello')\nprint('world')")
    
    result = analyze_directory(temp_dir)
    assert result["total_files"] == 1
    assert result["total_lines"] == 2
    assert ".py" in result["by_extension"]
    assert result["by_extension"][".py"]["files"] == 1
    assert result["by_extension"][".py"]["lines"] == 2


def test_analyze_directory_multiple_files(temp_dir):
    """Test analyzing a directory with multiple files."""
    # Create multiple files
    (Path(temp_dir) / "file1.py").write_text("line1\nline2")
    (Path(temp_dir) / "file2.py").write_text("line1\nline2\nline3")
    (Path(temp_dir) / "file3.js").write_text("console.log('test');")
    
    result = analyze_directory(temp_dir)
    assert result["total_files"] == 3
    assert result["total_lines"] == 6  # 2 + 3 + 1
    assert ".py" in result["by_extension"]
    assert ".js" in result["by_extension"]
    assert result["by_extension"][".py"]["files"] == 2
    assert result["by_extension"][".js"]["files"] == 1


def test_analyze_directory_nested(temp_dir):
    """Test analyzing a nested directory structure."""
    # Create nested structure
    subdir = Path(temp_dir) / "subdir"
    subdir.mkdir()
    
    (Path(temp_dir) / "root.py").write_text("root")
    (subdir / "nested.py").write_text("nested\nfile")
    
    result = analyze_directory(temp_dir)
    assert result["total_files"] == 2
    assert result["total_lines"] == 3  # 1 + 2


def test_analyze_directory_skips_git(temp_dir):
    """Test that .git directory is skipped."""
    # Create .git directory with files
    git_dir = Path(temp_dir) / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("git config data")
    
    # Create regular file
    (Path(temp_dir) / "file.py").write_text("code")
    
    result = analyze_directory(temp_dir)
    # Should only count the regular file, not .git contents
    assert result["total_files"] == 1
    assert result["total_lines"] == 1


def test_analyze_directory_skips_node_modules(temp_dir):
    """Test that node_modules directory is skipped."""
    node_modules = Path(temp_dir) / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.js").write_text("package data")
    
    (Path(temp_dir) / "file.py").write_text("code")
    
    result = analyze_directory(temp_dir)
    assert result["total_files"] == 1


def test_analyze_directory_invalid_path():
    """Test analyzing a non-existent path."""
    result = analyze_directory("/nonexistent/path/12345")
    assert result["total_files"] == 0
    assert result["total_lines"] == 0
    assert result["by_extension"] == {}
