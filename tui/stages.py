"""Stage screens for RepoLens TUI onboarding flow."""

import asyncio
from typing import Optional, Callable
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Input
from textual.containers import VerticalScroll

from tui.components import RepoLensHeader, RepoLensMenu
from tui.utils import validate_directory_path, validate_github_url, open_file_manager


class Stage1SourceSelection(Screen):
    """Stage 1: Source selection screen."""
    
    # TODO: Add keyboard shortcuts for menu navigation
    # TODO: Implement smooth transitions between menu items
    # TODO: Add help text tooltip system
    
    def __init__(self, on_selection: Callable[[str], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_selection = on_selection
        self.selected_index = 0
        self.menu_items = [
            ("01", "Local Directory"),
            ("02", "GitHub Repository"),
            ("00", "Exit"),
        ]
    
    def compose(self) -> ComposeResult:
        """Compose the stage."""
        # TODO: Optimize screen composition performance
        # TODO: Add responsive layout for different terminal sizes
        with VerticalScroll():
            yield RepoLensHeader(id="header")
            yield Static(
                "\nSelect the source for analysis:\n\n"
                "• Local Directory: Analyze a directory on your local filesystem\n"
                "• GitHub Repository: Clone and analyze a repository from GitHub\n",
                id="description"
            )
            yield RepoLensMenu(self.menu_items, self.selected_index, id="menu")
    
    def on_key(self, event) -> None:
        """Handle keyboard input."""
        # TODO: Add support for arrow key navigation
        # TODO: Implement Enter key selection
        # TODO: Add Escape key handling
        if event.key == "1" or (event.key == "enter" and self.selected_index == 0):
            self.on_selection("local")
        elif event.key == "2" or (event.key == "enter" and self.selected_index == 1):
            self.on_selection("github")
        elif event.key == "0" or (event.key == "enter" and self.selected_index == 2):
            self.on_selection("exit")
        elif event.key == "up":
            self.selected_index = max(0, self.selected_index - 1)
            self.query_one("#menu").set_selected(self.selected_index)
        elif event.key == "down":
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
            self.query_one("#menu").set_selected(self.selected_index)


class Stage2Input(Screen):
    """Stage 2: Input screen for directory path or GitHub URL."""
    
    # TODO: Add path autocomplete functionality
    # TODO: Implement input history for previous paths
    # TODO: Add file browser integration
    
    def __init__(self, source_type: str, on_submit: Callable[[str], None], on_exit: Callable[[], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_type = source_type
        self.on_submit = on_submit
        self.on_exit = on_exit
        self.error_message: Optional[str] = None
    
    def compose(self) -> ComposeResult:
        """Compose the stage."""
        # TODO: Add input validation feedback UI
        # TODO: Implement input suggestions
        # TODO: Add paste support for URLs/paths
        with VerticalScroll():
            yield RepoLensHeader(id="header")
            if self.source_type == "local":
                prompt_text = "\nEnter the path to the directory to analyze:"
                placeholder = "/path/to/directory"
            else:
                prompt_text = "\nEnter the GitHub repository URL:"
                placeholder = "https://github.com/user/repo"
            
            yield Static(prompt_text, id="prompt")
            yield Input(placeholder=placeholder, id="input")
            yield Static("", id="error")
            yield Static("\n00. Exit", id="exit_option")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        # TODO: Add input sanitization
        # TODO: Implement async validation
        value = event.value.strip()
        
        if not value:
            self.error_message = "Input cannot be empty"
            self.query_one("#error").update(self.error_message)
            return
        
        if self.source_type == "local":
            is_valid, error = validate_directory_path(value)
        else:
            is_valid, error = validate_github_url(value)
        
        if not is_valid:
            self.error_message = error or "Invalid input"
            self.query_one("#error").update(self.error_message)
            return
        
        self.on_submit(value)
    
    def on_key(self, event) -> None:
        """Handle keyboard input."""
        # TODO: Add keyboard shortcuts
        if event.key == "0":
            self.on_exit()


class Stage3OutputFormat(Screen):
    """Stage 3: Output format selection screen."""
    
    # TODO: Add format preview functionality
    # TODO: Implement format comparison view
    # TODO: Add format recommendations based on use case
    
    def __init__(self, on_selection: Callable[[str], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_selection = on_selection
        self.selected_index = 0
        self.menu_items = [
            ("01", "Markdown (Recommended & Descriptive)"),
            ("02", "JSON (Descriptive)"),
            ("03", "CSV (Raw Data Only)"),
            ("00", "Exit"),
        ]
    
    def compose(self) -> ComposeResult:
        """Compose the stage."""
        # TODO: Add format examples display
        # TODO: Implement format feature comparison
        with VerticalScroll():
            yield RepoLensHeader(id="header")
            yield Static(
                "\nSelect the output format:\n\n"
                "• Markdown: Human-readable report with insights and recommendations\n"
                "• JSON: Structured data format for programmatic processing\n"
                "• CSV: Raw metrics in tabular format\n",
                id="description"
            )
            yield RepoLensMenu(self.menu_items, self.selected_index, id="menu")
    
    def on_key(self, event) -> None:
        """Handle keyboard input."""
        # TODO: Add keyboard navigation improvements
        if event.key == "1" or (event.key == "enter" and self.selected_index == 0):
            self.on_selection("md")
        elif event.key == "2" or (event.key == "enter" and self.selected_index == 1):
            self.on_selection("json")
        elif event.key == "3" or (event.key == "enter" and self.selected_index == 2):
            self.on_selection("csv")
        elif event.key == "0" or (event.key == "enter" and self.selected_index == 3):
            self.on_selection("exit")
        elif event.key == "up":
            self.selected_index = max(0, self.selected_index - 1)
            self.query_one("#menu").set_selected(self.selected_index)
        elif event.key == "down":
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
            self.query_one("#menu").set_selected(self.selected_index)


class Stage4OutputDirectory(Screen):
    """Stage 4: Output directory selection screen."""
    
    # TODO: Add directory browser widget
    # TODO: Implement directory creation confirmation
    # TODO: Add path validation feedback
    
    def __init__(self, on_selection: Callable[[Optional[str]], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_selection = on_selection
        self.selected_index = 0
        self.menu_items = [
            ("01", "Default (/Reports)"),
            ("02", "Custom Directory"),
            ("00", "Exit"),
        ]
        self.custom_path: Optional[str] = None
        self.error_message: Optional[str] = None
    
    def compose(self) -> ComposeResult:
        """Compose the stage."""
        # TODO: Add directory preview
        # TODO: Implement path suggestions
        with VerticalScroll():
            yield RepoLensHeader(id="header")
            yield Static(
                "\nSelect output directory:\n",
                id="description"
            )
            yield RepoLensMenu(self.menu_items, self.selected_index, id="menu")
            yield Static("", id="custom_prompt")
            yield Static("", id="error")
    
    def on_key(self, event) -> None:
        """Handle keyboard input."""
        # TODO: Add better keyboard navigation
        if event.key == "1" or (event.key == "enter" and self.selected_index == 0):
            self.on_selection(None)  # Default directory
        elif event.key == "2":
            self.selected_index = 1
            self.query_one("#menu").set_selected(self.selected_index)
            self.refresh()
        elif event.key == "0" or (event.key == "enter" and self.selected_index == 2):
            self.on_selection("exit")
        elif event.key == "up":
            self.selected_index = max(0, self.selected_index - 1)
            self.query_one("#menu").set_selected(self.selected_index)
            self.refresh()
        elif event.key == "down":
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
            self.query_one("#menu").set_selected(self.selected_index)
            self.refresh()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle custom directory input."""
        # TODO: Add path validation
        # TODO: Implement directory creation
        from pathlib import Path
        
        value = event.value.strip()
        
        if not value:
            self.error_message = "Path cannot be empty"
            self.query_one("#error").update(self.error_message)
            return
        
        path_obj = Path(value)
        
        # Check if parent directory exists and is writable
        if not path_obj.parent.exists():
            self.error_message = "Parent directory does not exist"
            self.query_one("#error").update(self.error_message)
            return
        
        # Create directory if it doesn't exist
        if not path_obj.exists():
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.error_message = f"Cannot create directory: {str(e)}"
                self.query_one("#error").update(self.error_message)
                return
        
        if not path_obj.is_dir():
            self.error_message = "Path is not a directory"
            self.query_one("#error").update(self.error_message)
            return
        
        self.on_selection(str(path_obj.absolute()))


class Stage5Processing(Screen):
    """Stage 5: Processing screen with animated progress."""
    
    # TODO: Add cancel button for long-running operations
    # TODO: Implement progress percentage display
    # TODO: Add estimated time remaining
    
    def __init__(self, on_complete: Callable[[dict, str], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_complete = on_complete
        self.progress_messages = [
            "Scanning repository...",
            "Analyzing structure...",
            "Computing insights...",
            "Generating report...",
        ]
        self.current_message_index = 0
    
    def compose(self) -> ComposeResult:
        """Compose the stage."""
        # TODO: Add progress bar styling
        # TODO: Implement spinner animation
        with VerticalScroll():
            yield RepoLensHeader(id="header")
            yield Static("\n⏳ Processing...\n", id="status", classes="processing")
            yield Static("Progress: 0%", id="progress")


class Stage6Success(Screen):
    """Stage 6: Success screen with results."""
    
    # TODO: Add report preview functionality
    # TODO: Implement report sharing options
    # TODO: Add success animation
    
    def __init__(self, output_path: str, on_open_folder: Callable[[], None], 
                 on_run_again: Callable[[], None], on_exit: Callable[[], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_path = output_path
        self.on_open_folder = on_open_folder
        self.on_run_again = on_run_again
        self.on_exit = on_exit
        self.selected_index = 0
        self.menu_items = [
            ("01", "Open folder"),
            ("02", "Run again"),
            ("00", "Exit"),
        ]
    
    def compose(self) -> ComposeResult:
        """Compose the stage."""
        # TODO: Add file size and metadata display
        # TODO: Implement report statistics summary
        with VerticalScroll():
            yield RepoLensHeader(id="header")
            yield Static("\n✔ Report generated successfully\n", id="success_message", classes="success")
            yield Static(f"📁 Saved to: {self.output_path}\n", id="file_path")
            yield RepoLensMenu(self.menu_items, self.selected_index, id="menu")
    
    def on_key(self, event) -> None:
        """Handle keyboard input."""
        # TODO: Add keyboard shortcuts
        if event.key == "1" or (event.key == "enter" and self.selected_index == 0):
            self.on_open_folder()
        elif event.key == "2" or (event.key == "enter" and self.selected_index == 1):
            self.on_run_again()
        elif event.key == "0" or (event.key == "enter" and self.selected_index == 2):
            self.on_exit()
        elif event.key == "up":
            self.selected_index = max(0, self.selected_index - 1)
            self.query_one("#menu").set_selected(self.selected_index)
        elif event.key == "down":
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
            self.query_one("#menu").set_selected(self.selected_index)
