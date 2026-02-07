---
name: GitScope CLI Tool
overview: Build a lightweight, modular Python CLI tool for analyzing local directories and GitHub repositories. The tool counts files, lines, and characters, groups stats by extension, supports multiple languages, and exports JSON/CSV reports. Assumes Git CLI is pre-authenticated.
todos:
  - id: setup-structure
    content: Create project directory structure with all required files and folders
    status: completed
  - id: implement-config
    content: Implement config.py with skip directories and binary detection constants
    status: completed
  - id: implement-analyzer
    content: Implement analyzer.py with recursive directory scanning, line-by-line streaming, and extension grouping
    status: completed
  - id: implement-i18n
    content: Implement i18n.py and create language JSON files (en, es, ar)
    status: completed
  - id: implement-github
    content: Implement github.py for cloning repositories to temp directories and cleanup
    status: completed
  - id: implement-exporter
    content: Implement exporter.py for JSON and CSV export with timestamped filenames
    status: completed
  - id: implement-main
    content: Implement main.py CLI with argparse, orchestration logic, and formatted output
    status: completed
  - id: write-tests
    content: Write test_analyzer.py with pytest tests for core analyzer functionality
    status: completed
  - id: setup-dependencies
    content: Create requirements.txt and pyproject.toml with project metadata
    status: completed
  - id: write-readme
    content: Write concise README.md with installation, Git CLI setup instructions, and usage examples
    status: completed
---

# GitScope Implementation Plan

## Project Structure

Create the following file structure:

```
gitscope/
├── main.py              # CLI entry point with argparse
├── analyzer.py          # Core analysis engine
├── github.py            # GitHub repo cloning/cleanup
├── exporter.py          # JSON/CSV export handlers
├── i18n.py              # Internationalization loader
├── config.py            # Configuration constants
├── languages/
│   ├── en.json          # English translations
│   ├── es.json          # Spanish translations
│   └── ar.json          # Arabic translations
├── tests/
│   └── test_analyzer.py # Pytest test suite
├── README.md            # Installation and usage guide
├── requirements.txt     # Python dependencies
└── pyproject.toml       # Project metadata
```

## Implementation Details

### 1. config.py

- Define skip directories: `.git`, `node_modules`, `build`, `dist`
- Define binary file extensions or detection method
- Default language setting

### 2. analyzer.py

**Core Functions:**

- `is_binary_file(filepath: str) -> bool`: Detect binary files (check for null bytes or common binary extensions)
- `analyze_directory(path: str) -> dict`: Main analysis function
  - Recursively scan directory
  - Skip configured directories
  - Stream files line-by-line to count lines/characters (memory efficient)
  - Group statistics by file extension
  - Return structured dict: `{total_files, total_lines, total_chars, by_extension: {...}}`

**Key Requirements:**

- No printing/logging inside analyzer module
- Pure functions with type hints
- Handle encoding errors gracefully (skip problematic files)

### 3. github.py

**Functions:**

- `clone_repository(repo_url: str) -> str`: Clone repo to temp directory, return path
- `cleanup_temp_directory(path: str) -> None`: Remove temp directory
- Use `subprocess` or `GitPython` for cloning
- Handle clone failures with clear error messages

### 4. i18n.py

**Functions:**

- `load_language(lang: str) -> dict`: Load JSON from `languages/{lang}.json`
- `get_text(key: str, lang: str = "en") -> str`: Get translated text with English fallback
- Cache loaded languages to avoid repeated file reads

### 5. exporter.py

**Functions:**

- `export_json(data: dict, output_path: str = None) -> str`: Export to JSON with timestamped filename
- `export_csv(data: dict, output_path: str = None) -> str`: Export to CSV with timestamped filename
- Filename format: `gitscope_report_YYYYMMDD_HHMMSS.{json|csv}`
- Handle nested data structures in CSV export (flatten extension stats)

### 6. main.py

**CLI Arguments:**

- `--dir PATH`: Analyze local directory
- `--repo URL`: Clone and analyze GitHub repository
- `--lang {en,es,ar}`: Select interface language (default: en)
- `--export {json,csv}`: Export format (optional)

**Implementation Flow:**

1. Parse arguments with `argparse`
2. Validate that either `--dir` or `--repo` is provided (mutually exclusive)
3. Load i18n translations based on `--lang`
4. If `--repo`: clone repository, analyze, cleanup
5. If `--dir`: analyze directly
6. Format and print summary using i18n strings
7. If `--export` specified: call exporter module
8. Handle errors gracefully with translated messages

**Output Format:**

Print formatted summary table:

- Total files, lines, characters
- Top extensions by file count
- Top extensions by line count

### 7. languages/*.json

**Structure for each language file:**

```json
{
  "summary": "Project Summary",
  "files": "Files",
  "lines": "Lines",
  "characters": "Characters",
  "by_extension": "By Extension",
  "top_extensions": "Top Extensions",
  "analyzing": "Analyzing...",
  "cloning": "Cloning repository...",
  "error": "Error",
  "invalid_path": "Invalid path",
  "clone_failed": "Failed to clone repository"
}
```

### 8. tests/test_analyzer.py

**Test Cases:**

- Create temporary test directory structure
- Test file counting (including nested directories)
- Test line counting (various file types)
- Test character counting
- Test extension grouping
- Test skip directories functionality
- Test binary file detection
- Cleanup temporary files after tests

Use `pytest` fixtures for temporary directories.

### 9. requirements.txt

**Dependencies:**

- `pytest>=7.0.0` (for testing)
- `tqdm>=4.65.0` (optional: progress bar)
- `colorama>=0.4.6` (optional: colored output)

Note: Use standard library for core functionality (subprocess, json, csv, pathlib).

### 10. pyproject.toml

**Project Metadata:**

- Project name: `gitscope`
- Version: `0.1.0`
- Python version: `>=3.11`
- Author and description
- Entry point: `gitscope = gitscope.main:main`

### 11. README.md

**Required Sections:**

1. **Installation**

   - `pip install -e .` or `pip install -r requirements.txt`
   - Python 3.11+ requirement

2. **Git CLI Setup (REQUIRED)**
   ```bash
   git config --global user.name "your-name"
   git config --global user.email "your-email"
   gh auth login
   ```

3. **Usage Examples**

   - Analyze local directory: `python main.py --dir /path/to/repo`
   - Analyze GitHub repo: `python main.py --repo https://github.com/user/repo`
   - With language: `python main.py --dir . --lang es`
   - Export JSON: `python main.py --dir . --export json`

4. **Export Example**

   - Show sample output filename and format

Keep README concise (max 50 lines).

## Architecture Flow

```
main.py (CLI)
    ↓
    ├─→ github.py (clone if --repo)
    │       ↓
    │   temp directory
    │       ↓
    ├─→ analyzer.py (analyze directory)
    │       ↓
    │   structured data dict
    │       ↓
    ├─→ i18n.py (load translations)
    │       ↓
    ├─→ Format & print summary
    │       ↓
    └─→ exporter.py (if --export specified)
            ↓
        JSON/CSV file
```

## Data Structure

**Analyzer Output Format:**

```python
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
        ".js": { ... },
        ...
    }
}
```

## Optional Enhancements

If simple to implement:

1. **Progress Bar**: Use `tqdm` in `analyzer.py` when processing large directories
2. **Colored Output**: Use `colorama`` in `main.py` for summary highlighting
3. **Extension Leaderboard**: Sort and display top 10 extensions by file count
4. **Top Largest Files**: Track and display top 5 largest files (by character count)

Only add if implementation is straightforward (< 20 lines each).

## Implementation Order

1. Create project structure (directories and empty files)
2. Implement `config.py` (constants)
3. Implement `analyzer.py` (core logic)
4. Implement `i18n.py` and language JSON files
5. Implement `github.py`
6. Implement `exporter.py`
7. Implement `main.py` (CLI orchestration)
8. Write `test_analyzer.py`
9. Create `requirements.txt` and `pyproject.toml`
10. Write `README.md`
11. Test end-to-end workflow

## Key Implementation Notes

- **Memory Efficiency**: Stream files line-by-line using generators, don't load entire files
- **Error Handling**: Gracefully skip files with encoding errors, log warnings
- **Type Safety**: Use type hints throughout, enable mypy checking
- **Clean Architecture**: Each module is independent and testable
- **No Auth**: Assume Git CLI is pre-configured, no authentication code
- **Binary Detection**: Check first 8192 bytes for null bytes, or use extension whitelist