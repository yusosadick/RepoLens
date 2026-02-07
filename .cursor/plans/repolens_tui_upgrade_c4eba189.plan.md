---
name: RepoLens TUI Upgrade
overview: Transform RepoLens into a professional interactive terminal GUI with stage-based onboarding while preserving CLI functionality
todos:
  - id: setup-dependencies
    content: Update requirements.txt with textual and rich dependencies (no prompt-toolkit)
    status: completed
  - id: create-tui-structure
    content: Create tui/ directory with __init__.py, app.py, components.py, stages.py, utils.py
    status: completed
  - id: implement-utils
    content: Implement tui/utils.py with ASCII header generator and utility functions
    status: completed
  - id: implement-components
    content: Implement tui/components.py with header, footer, and menu components
    status: completed
  - id: implement-stages
    content: Implement all 6 stage screens in tui/stages.py (source selection, input, format, directory, processing, success)
    status: completed
  - id: implement-app
    content: Implement tui/app.py with Textual App class, state management, and stage navigation
    status: completed
  - id: update-exporter
    content: Update exporter.py to support custom output directories
    status: completed
  - id: refactor-main
    content: Refactor main.py to support interactive mode (default), direct CLI mode, and help mode
    status: completed
  - id: test-interactive
    content: Test interactive TUI mode end-to-end with all stages
    status: completed
  - id: test-cli-compatibility
    content: Verify direct CLI mode and help mode still work correctly
    status: completed
  - id: update-readme
    content: Update README.md with documentation for all three modes and usage examples
    status: completed
  - id: add-todo-comments
    content: Add 50 unique TODO comments across codebase covering UX, performance, and architecture improvements
    status: completed
---

# RepoLens TUI Upgrade Plan

## Overview

Transform RepoLens into a professional interactive terminal GUI using Textual and Rich. This is a strict implementation task that extends the existing project structure. The upgrade adds a guided onboarding flow with premium terminal aesthetics while preserving all existing CLI functionality. No architecture redesign allowed.

## Architecture

The implementation follows a stage-based navigation model:

```
main.py (entry point)
├── Interactive Mode (default) → tui/app.py
│   ├── Stage 1: Source Selection
│   ├── Stage 2: Input (directory/repo URL)
│   ├── Stage 3: Output Format
│   ├── Stage 4: Output Directory
│   ├── Stage 5: Processing (with animations)
│   └── Stage 6: Success Screen
├── Direct CLI Mode (--dir/--repo flags)
└── Help Mode (--help)
```

## File Structure

### New Files

1. **`tui/__init__.py`** - TUI package initialization
2. **`tui/app.py`** - Main Textual application with stage navigation
3. **`tui/components.py`** - Reusable UI components (header, footer, menu)
4. **`tui/stages.py`** - Individual stage screens
5. **`tui/utils.py`** - TUI utilities (ASCII art, formatting)

### Modified Files

1. **`main.py`** - Refactor to support three modes:

   - Interactive (default, no args)
   - Direct CLI (--dir/--repo)
   - Help (--help)

2. **`requirements.txt`** - Add Textual and Rich (no Prompt Toolkit)
3. **`README.md`** - Document new TUI features and modes
4. **`exporter.py`** - Add support for custom output directories

## Implementation Details

### 1. Dependencies (`requirements.txt`)

Add:

- `textual>=0.40.0` (primary TUI framework)
- `rich>=13.0.0` (rendering and styling)

Do NOT use Prompt Toolkit. Use Textual's built-in Input widgets.

### 2. TUI Application (`tui/app.py`)

Create a Textual `App` class that manages stage navigation:

- **State Management**: Track current stage, user selections (source type, input path, format, output dir)
- **Stage Router**: Navigate between stages based on user selections
- **Header/Footer**: Persistent header with ASCII logo and footer on all screens
- **Navigation**: Number-based menu selection (01, 02, 00 for exit)

Key methods:

- `on_mount()` - Initialize to Stage 1
- `go_to_stage(stage_num)` - Navigate to specific stage
- `handle_selection(choice)` - Process user menu selections
- `run_analysis()` - Execute analysis with progress tracking

### 3. Stage Screens (`tui/stages.py`)

Each stage is a Textual `Screen` widget:

**Stage 1 - Source Selection:**

- Menu: "01. Local Directory", "02. GitHub Repository", "00. Exit"
- Description text explaining the difference between local and GitHub options
- Header and footer present

**Stage 2 - Input:**

- If Local: Prompt for directory path (with validation)
- If GitHub: Prompt for repo URL (with validation)
- Always include Exit option
- Uses Textual `Input` widget for text input

**Stage 3 - Output Format:**

- Menu: "01. Markdown (Recommended & Descriptive)", "02. JSON (Descriptive)", "03. CSV (Raw Data Only)", "00. Exit"
- Short explanation under menu

**Stage 4 - Output Directory:**

- Menu: "01. Default (/GeneratedReports)", "02. Custom Directory", "00. Exit"
- If custom: Prompt for path

**Stage 5 - Processing:**

- Beautiful animated processing with spinner
- Staged messages: "Scanning repository...", "Analyzing structure...", "Computing insights...", "Generating report..."
- Rich `Progress` bar with animations
- Uses Textual's async capabilities for smooth animation
- Must feel premium and polished

**Stage 6 - Success:**

- Success message: "✔ Report generated successfully"
- File path display: "📁 Saved to: <path>"
- Menu: "01. Open folder", "02. Run again", "00. Exit"
- "Open folder" uses platform-specific file manager (Linux: `xdg-open`, macOS: `open`, Windows: `explorer`)

### 4. UI Components (`tui/components.py`)

**Header Component:**

- ASCII art banner (figlet-generated, exact format required):
```
 ____  _____ ____       _     _____ _   _ ____  
|  _ \| ____|  _ \ ___ | |   | ____| \ | / ___| 
| |_) |  _| | |_) / _ \| |   |  _| |  \| \___ \ 
|  _ <| |___|  __/ (_) | |___| |___| |\  |___) |
|_| \_\_____|_|   \___/|_____|_____|_| \_|____/
```

- Subtitle: "🔍 RepoLens — Repository Intelligence Engine"
- User identity: "User: <system username>" (from `os.getenv('USER')` or `getpass.getuser()`)
- Mode indicator: "Mode: Interactive"
- Footer text: "💻 web & mobile applications and backend systems. I love coding, lets connect instagram.com/yuso_sadick/ ☕ Buy me a coffee buymeacoffee.com/yuso_sadick"

**Footer Component:**

- Footer is integrated into header layout (see Header Component above)

**Menu Component:**

- Numbered list with consistent styling
- Highlight selected option
- Exit option always at bottom (00)

### 5. Main Entry Point (`main.py`)

Refactor `main()` to support three modes:

```python
def main():
    parser = argparse.ArgumentParser(...)
    
    # Keep existing args but make them optional
    parser.add_argument("--dir", ...)
    parser.add_argument("--repo", ...)
    parser.add_argument("--report", choices=["md", "json", "csv"])
    parser.add_argument("--output-dir", ...)
    
    args = parser.parse_args()
    
    # Mode detection
    if args.help or (not args.dir and not args.repo):
        if args.help:
            # Show help and exit
            parser.print_help()
            return
        else:
            # Launch interactive TUI
            from tui.app import RepoLensApp
            app = RepoLensApp()
            app.run()
    else:
        # Direct CLI mode (existing logic)
        # ... existing analysis code ...
```

### 6. Exporter Updates (`exporter.py`)

Modify export functions to accept `output_dir` parameter:

- `export_json(data, output_path=None, output_dir=None)`
- `export_csv(data, output_path=None, output_dir=None)`
- `export_markdown(content, output_path=None, output_dir=None)`

If `output_dir` provided, create directory if needed and save there. Default to current directory.

### 7. ASCII Header Design (`tui/utils.py`)

Create ASCII art generator function using exact figlet banner:

```python
REPOLENS_BANNER = """
 ____  _____ ____       _     _____ _   _ ____  
|  _ \| ____|  _ \ ___ | |   | ____| \ | / ___| 
| |_) |  _| | |_) / _ \| |   |  _| |  \| \___ \ 
|  _ <| |___|  __/ (_) | |___| |___| |\  |___) |
|_| \_\_____|_|   \___/|_____|_____|_| \_|____/
"""

def generate_header() -> str:
    """Generate RepoLens ASCII header banner with exact format."""
    # Use figlet output exactly as provided
    # Include subtitle, user info, mode, and footer text
    # Use Rich for colored output
```

Header structure (exact format required):

```
 ____  _____ ____       _     _____ _   _ ____  
|  _ \| ____|  _ \ ___ | |   | ____| \ | / ___| 
| |_) |  _| | |_) / _ \| |   |  _| |  \| \___ \ 
|  _ <| |___|  __/ (_) | |___| |___| |\  |___) |
|_| \_\_____|_|   \___/|_____|_____|_| \_|____/

🔍 RepoLens — Repository Intelligence Engine
User: <system username>
Mode: Interactive

💻 web & mobile applications and backend systems. 

I love coding, lets connect  instagram.com/yuso_sadick/
   ☕ Buy me a coffee  buymeacoffee.com/yuso_sadick
```

This header must render on EVERY screen.

### 8. Processing Animation (`tui/stages.py` - Processing Stage)

Implement async processing with Rich progress and exact messages:

```python
async def process_analysis(self):
    """Run analysis with animated progress."""
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing...", total=100)
        
        # Step 1: Scanning repository
        progress.update(task, advance=25, description="[cyan]Scanning repository...")
        await asyncio.sleep(0.5)
        
        # Step 2: Analyzing structure
        progress.update(task, advance=25, description="[cyan]Analyzing structure...")
        await asyncio.sleep(0.5)
        
        # Step 3: Computing insights
        progress.update(task, advance=25, description="[cyan]Computing insights...")
        await asyncio.sleep(0.5)
        
        # Step 4: Generating report
        progress.update(task, advance=25, description="[cyan]Generating report...")
        await asyncio.sleep(0.5)
```

Use Textual's `worker` API for actual analysis work to prevent blocking. The animation must feel premium and polished.

### 9. Input Validation

**Directory Path Validation:**

- Check if path exists
- Check if it's a directory
- Show error message if invalid, allow retry

**GitHub URL Validation:**

- Basic URL format check
- GitHub domain validation
- Show error message if invalid, allow retry

**Output Directory Validation:**

- Check if path exists (if not, offer to create)
- Check write permissions
- Create directory if needed

### 10. State Management (`tui/app.py`)

Track user selections in app state:

```python
class AppState:
    source_type: Optional[str] = None  # "local" or "github"
    input_path: Optional[str] = None  # directory path or repo URL
    output_format: Optional[str] = None  # "md", "json", "csv"
    output_dir: Optional[str] = None  # custom output directory
    current_stage: int = 1
    analysis_results: Optional[Dict] = None
    output_file_path: Optional[str] = None
```

### 11. Error Handling

- **Network errors** (GitHub clone): Show friendly error, allow retry or exit
- **File system errors**: Show error message, allow retry
- **Analysis errors**: Show error, allow to go back or exit
- **Keyboard interrupt**: Graceful exit with cleanup

### 12. README Updates (`README.md`)

Add sections:

**Interactive Mode:**

````markdown
### Interactive Mode (Default)

Simply run RepoLens without arguments to launch the interactive terminal GUI:

```bash
repolens
````

This launches a beautiful stage-based onboarding flow that guides you through:

- Source selection (local directory or GitHub repository)
- Input configuration
- Output format selection
- Output directory selection
- Processing with live progress
- Success screen with options
````

**One-Command CLI Mode:**

```markdown
### One-Command CLI Mode

For automation and scripting, use direct CLI arguments:

```bash
# Analyze local directory
repolens --dir /path/to/repo --report md

# Analyze GitHub repository
repolens --repo https://github.com/user/repo --report json --output-dir ./reports
````


All existing CLI functionality is preserved.

````

**Help Mode:**

```markdown
### Help / Manual

View CLI usage and options:

```bash
repolens --help
```

This shows command-line options only (no GUI).
````

Add screenshots section placeholder for TUI examples.

### 13. Platform-Specific Features

**File Manager Opening:**

```python

import platform

import subprocess

def open_file_manager(path: str) -> None:

"""Open file manager at given path."""

system = platform.system()

if system == "Linux":

subprocess.run(["xdg-open", path])

elif system == "Darwin":  # macOS

subprocess.run(["open", path])

elif system == "Windows":

subprocess.run(["explorer", path])

````

### 14. Default Output Directory

Create `GeneratedReports` directory in current working directory if default option selected. Use `pathlib.Path` for cross-platform compatibility.

### 15. TODO Comments Requirement

Add 50 internal TODO comments across the codebase:

- Each TODO must be unique
- Reference improvements, optimizations, or future enhancements
- Cover UX improvements, performance optimizations, architecture considerations
- Simulate real development roadmap
- Do NOT explain them in comments - just generate naturally in code
- Distribute across all new files (tui/app.py, tui/stages.py, tui/components.py, tui/utils.py, main.py, exporter.py)

## Implementation Order

1. **Phase 1: Dependencies & Structure**

   - Update `requirements.txt`
   - Create `tui/` directory structure
   - Create `tui/__init__.py`

2. **Phase 2: Core Components**

   - Implement `tui/utils.py` (ASCII header, utilities)
   - Implement `tui/components.py` (header, footer, menu components)

3. **Phase 3: Stage Screens**

   - Implement `tui/stages.py` (all 6 stages)
   - Test each stage individually

4. **Phase 4: Application Logic**

   - Implement `tui/app.py` (main app with navigation)
   - Wire up stage transitions
   - Implement state management

5. **Phase 5: Integration**

   - Update `exporter.py` for custom output directories
   - Refactor `main.py` for three-mode support
   - Test interactive mode end-to-end

6. **Phase 6: CLI Mode**

   - Ensure direct CLI mode still works
   - Test help mode
   - Verify backward compatibility

7. **Phase 7: Documentation & TODOs**

   - Update `README.md` with new features
   - Add usage examples
   - Document all three modes
   - Add 50 TODO comments across codebase

## Testing Checklist

- [ ] Interactive mode launches correctly
- [ ] All 6 stages render properly
- [ ] Navigation between stages works
- [ ] Input validation works (directory, URL, output path)
- [ ] Processing animation displays correctly
- [ ] Analysis completes successfully
- [ ] Reports are generated in correct location
- [ ] Success screen shows correct file path
- [ ] "Open folder" works on all platforms
- [ ] "Run another analysis" resets to Stage 1
- [ ] Exit option works from all stages
- [ ] Direct CLI mode still works
- [ ] Help mode shows correct usage
- [ ] Error handling works gracefully
- [ ] Keyboard interrupt handled properly

## Critical Implementation Rules

- **NO architecture redesign** - Only extend existing structure
- **NO new folders** unless absolutely required
- **NO alternate flows** - Follow exact stage flow specified
- **Modify existing project only** - Do not create new project structure
- **Exact banner required** - Use figlet output exactly as provided
- **Exact header layout** - Use specified format with user info and footer text
- **50 TODO comments** - Distribute naturally across codebase
- **Textual + Rich only** - No Prompt Toolkit
- **Exit option on EVERY screen** - Consistent navigation
- **Premium feel** - Tight spacing, clean typography, elegant layout
- **No clutter** - Professional, polished terminal application

## Notes

- Textual requires Python 3.8+, which aligns with RepoLens's Python 3.11+ requirement
- Rich is already used indirectly via Textual, but we add it explicitly for advanced styling
- All existing functionality must be preserved
- The TUI should feel premium and polished, not cluttered
- Use consistent spacing and typography throughout
- Emoji usage should be minimal but effective (🔍 for lens, ☕ for coffee, ✔ for success)
- Readable in small terminals - responsive layout