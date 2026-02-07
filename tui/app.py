"""Main Textual application for RepoLens TUI."""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from textual.app import App, ComposeResult
from textual.worker import Worker, get_current_worker
from textual.widgets import Static

from tui.stages import (
    Stage1SourceSelection,
    Stage2Input,
    Stage3OutputFormat,
    Stage4OutputDirectory,
    Stage5Processing,
    Stage6Success,
)
from tui.utils import open_file_manager
from analyzer import analyze_directory
from utils import clone_repository, cleanup_temp_directory
from reporter import export_json, export_csv, export_markdown
import insights
import reporter

# TODO: Add import error handling
# TODO: Implement lazy imports for performance


@dataclass
class AppState:
    """Application state management."""
    
    # TODO: Add state persistence for session recovery
    # TODO: Implement state validation
    # TODO: Add state history for undo/redo
    
    source_type: Optional[str] = None  # "local" or "github"
    input_path: Optional[str] = None  # directory path or repo URL
    output_format: Optional[str] = None  # "md", "json", "csv"
    output_dir: Optional[str] = None  # custom output directory
    current_stage: int = 1
    analysis_results: Optional[Dict[str, Any]] = None
    output_file_path: Optional[str] = None
    temp_dir: Optional[str] = None


class RepoLensApp(App):
    """Main RepoLens TUI application."""
    
    CSS = """
    Screen {
        background: #1a1a2e;
    }
    
    VerticalScroll {
        height: 100%;
        width: 100%;
        background: #1a1a2e;
    }
    
    #header {
        height: auto;
        padding: 1 2;
        width: 100%;
        color: #00d9ff;
    }
    
    .error {
        color: #ff6b6b;
    }
    .success {
        color: #4ecdc4;
    }
    .processing {
        color: #00d9ff;
    }
    
    Static {
        width: 100%;
        height: auto;
        padding: 0 2;
    }
    
    #menu {
        margin-top: 1;
        width: 100%;
        padding: 0 2;
    }
    
    #description {
        width: 100%;
        padding: 0 2;
    }
    
    Input {
        width: 80%;
        margin: 1 2;
    }
    """
    
    # TODO: Add theme customization support
    # TODO: Implement app configuration file
    # TODO: Add keyboard shortcut customization
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = AppState()
        self.processing_screen: Optional[Stage5Processing] = None
    
    def on_mount(self) -> None:
        """Mount handler to push initial screen."""
        # TODO: Add splash screen option
        # TODO: Implement screen caching
        # Push Stage 1 as the initial screen
        self.push_screen(Stage1SourceSelection(on_selection=self.handle_stage1_selection))
    
    def go_to_stage(self, stage_num: int) -> None:
        """
        Navigate to a specific stage.
        
        Args:
            stage_num: Stage number (1-6)
        """
        # TODO: Add stage transition animations
        # TODO: Implement stage history tracking
        # TODO: Add stage validation before navigation
        
        self.state.current_stage = stage_num
        
        if stage_num == 1:
            screen = Stage1SourceSelection(on_selection=self.handle_stage1_selection)
        elif stage_num == 2:
            screen = Stage2Input(
                source_type=self.state.source_type or "local",
                on_submit=self.handle_stage2_submit,
                on_exit=self.handle_exit
            )
        elif stage_num == 3:
            screen = Stage3OutputFormat(on_selection=self.handle_stage3_selection)
        elif stage_num == 4:
            screen = Stage4OutputDirectory(on_selection=self.handle_stage4_selection)
        elif stage_num == 5:
            self.processing_screen = Stage5Processing(on_complete=self.handle_processing_complete)
            screen = self.processing_screen
        elif stage_num == 6:
            screen = Stage6Success(
                output_path=self.state.output_file_path or "",
                on_open_folder=self.handle_open_folder,
                on_run_again=self.handle_run_again,
                on_exit=self.handle_exit
            )
        else:
            return
        
        # Push screen (modal approach) - this will show on top
        self.push_screen(screen)
    
    def handle_stage1_selection(self, choice: str) -> None:
        """Handle Stage 1 selection."""
        # TODO: Add selection validation
        if choice == "exit":
            self.exit()
            return
        
        self.state.source_type = choice
        # Dismiss current screen and go to next
        self.pop_screen()
        self.go_to_stage(2)
    
    def handle_stage2_submit(self, value: str) -> None:
        """Handle Stage 2 input submission."""
        # TODO: Add input sanitization
        # TODO: Implement input caching
        self.state.input_path = value
        self.pop_screen()
        self.go_to_stage(3)
    
    def handle_stage3_selection(self, choice: str) -> None:
        """Handle Stage 3 format selection."""
        # TODO: Add format validation
        if choice == "exit":
            self.exit()
            return
        
        self.state.output_format = choice
        self.pop_screen()
        self.go_to_stage(4)
    
    def handle_stage4_selection(self, choice: Optional[str]) -> None:
        """Handle Stage 4 directory selection."""
        # TODO: Add directory validation
        # TODO: Implement directory creation confirmation
        if choice == "exit":
            self.exit()
            return
        
        if choice is None:
            # Default directory
            default_dir = Path.cwd() / "Reports"
            default_dir.mkdir(exist_ok=True)
            self.state.output_dir = str(default_dir.absolute())
        else:
            self.state.output_dir = choice
        
        self.pop_screen()
        self.go_to_stage(5)
        # Run analysis after screen is shown
        self.call_after_refresh(self.run_analysis)
    
    async def run_analysis(self) -> None:
        """Run the analysis with progress tracking."""
        # TODO: Add analysis cancellation support
        # TODO: Implement analysis progress persistence
        # TODO: Add error recovery mechanisms
        
        if not self.processing_screen:
            return
        
        analysis_path: Optional[str] = None
        temp_dir: Optional[str] = None
        
        try:
            # Update progress: Scanning repository
            self.processing_screen.query_one("#status", Static).update("[cyan]Scanning repository...[/cyan]")
            progress_widget = self.processing_screen.query_one("#progress", Static)
            progress_widget.update("[dim]Progress: 25%[/dim]")
            await asyncio.sleep(0.3)
            
            # Clone or use local directory
            if self.state.source_type == "github":
                temp_dir = clone_repository(self.state.input_path or "")
                analysis_path = temp_dir
                self.state.temp_dir = temp_dir
            else:
                analysis_path = self.state.input_path
            
            # Update progress: Analyzing structure
            self.processing_screen.query_one("#status", Static).update("[cyan]Analyzing structure...[/cyan]")
            progress_widget.update("[dim]Progress: 50%[/dim]")
            await asyncio.sleep(0.3)
            
            # Run analysis in worker to prevent blocking
            def analyze():
                return analyze_directory(analysis_path or "")
            
            worker = self.run_worker(analyze, thread=True)
            results = await worker.wait()
            self.state.analysis_results = results
            
            # Update progress: Computing insights
            self.processing_screen.query_one("#status", Static).update("[cyan]Computing insights...[/cyan]")
            progress_widget.update("[dim]Progress: 75%[/dim]")
            await asyncio.sleep(0.3)
            
            # Compute insights
            computed_insights = insights.compute_insights(results)
            computed_insights["ecosystem_breakdown"] = reporter.compute_ecosystem_breakdown(
                computed_insights, results
            )
            
            # Update progress: Generating report
            self.processing_screen.query_one("#status", Static).update("[cyan]Generating report...[/cyan]")
            progress_widget.update("[dim]Progress: 90%[/dim]")
            await asyncio.sleep(0.3)
            
            # Generate and export report
            output_path = self.generate_report(computed_insights, results, analysis_path or "")
            self.state.output_file_path = output_path
            
            # Complete progress
            progress_widget.update("[dim]Progress: 100%[/dim]")
            await asyncio.sleep(0.2)
            
            # Navigate to success screen
            self.call_after_refresh(lambda: self.go_to_stage(6))
            
        except Exception as e:
            # TODO: Add proper error handling UI
            # TODO: Implement error recovery options
            error_msg = f"Error during analysis: {str(e)}"
            self.processing_screen.query_one("#status", Static).update(f"[red]{error_msg}[/red]")
            await asyncio.sleep(2)
            # TODO: Add option to retry or go back
        finally:
            # Cleanup temp directory
            if temp_dir:
                cleanup_temp_directory(temp_dir)
    
    def generate_report(self, computed_insights: Dict[str, Any], results: Dict[str, Any], 
                       analysis_path: str) -> str:
        """
        Generate and export the report.
        
        Args:
            computed_insights: Computed insights dictionary
            results: Analysis results dictionary
            analysis_path: Path to analyzed repository
            
        Returns:
            Path to generated report file
        """
        # TODO: Add report generation options
        # TODO: Implement report templates
        # TODO: Add report customization
        # TODO: Add report format validation
        
        from pathlib import Path
        
        output_dir = Path(self.state.output_dir or Path.cwd() / "Reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        format_type = self.state.output_format or "md"
        
        # Determine repo_path for filename generation (use input_path which may be URL or local path)
        repo_path = self.state.input_path if self.state.input_path else analysis_path
        
        if format_type == "md":
            markdown_content = reporter.generate_markdown_report(
                results, computed_insights, repo_path, analysis_path
            )
            output_path = export_markdown(markdown_content, output_dir=str(output_dir), repo_path=repo_path)
        elif format_type == "json":
            output_path = export_json(results, output_dir=str(output_dir), repo_path=repo_path)
        else:  # csv
            output_path = export_csv(results, output_dir=str(output_dir), repo_path=repo_path)
        
        return output_path
    
    def handle_processing_complete(self, results: Dict[str, Any], output_path: str) -> None:
        """Handle processing completion (callback from processing screen)."""
        # TODO: Add completion validation
        # This is handled in run_analysis instead
    
    def handle_open_folder(self) -> None:
        """Handle open folder action."""
        # TODO: Add error handling for file manager
        # TODO: Implement cross-platform testing
        if self.state.output_file_path:
            output_dir = Path(self.state.output_file_path).parent
            open_file_manager(str(output_dir))
    
    def handle_run_again(self) -> None:
        """Handle run again action."""
        # TODO: Add state reset confirmation
        # TODO: Implement state history preservation
        self.state = AppState()
        self.pop_screen()
        # Reset to first stage
        self.call_after_refresh(lambda: self.go_to_stage(1))
    
    def handle_exit(self) -> None:
        """Handle exit action."""
        # TODO: Add exit confirmation
        # TODO: Implement cleanup on exit
        # TODO: Add session save option
        if self.state.temp_dir:
            cleanup_temp_directory(self.state.temp_dir)
        self.exit()
