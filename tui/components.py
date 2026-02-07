"""Reusable UI components for RepoLens TUI."""

from textual.widgets import Static
from textual.app import ComposeResult

from tui.utils import generate_header


class RepoLensHeader(Static):
    """Header component with ASCII banner and user info."""
    
    # TODO: Add theme support for header colors
    # TODO: Implement responsive header sizing for small terminals
    # TODO: Add animation support for header rendering
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        """Mount handler to set content."""
        header_text = generate_header()
        self.update(header_text)


class RepoLensMenu(Static):
    """Menu component with numbered options."""
    
    # TODO: Add keyboard navigation support
    # TODO: Implement menu item highlighting on hover
    # TODO: Add support for menu item icons
    
    def __init__(self, items: list[tuple[str, str]], selected_index: int = 0, *args, **kwargs):
        """
        Initialize menu.
        
        Args:
            items: List of (number, text) tuples
            selected_index: Index of currently selected item
        """
        super().__init__(*args, **kwargs)
        self.items = items
        self.selected_index = selected_index
    
    def on_mount(self) -> None:
        """Mount handler to set content."""
        self.update(self._generate_menu_text())
    
    def _generate_menu_text(self) -> str:
        """Generate menu text."""
        lines = []
        for i, (number, text) in enumerate(self.items):
            selected = i == self.selected_index
            prefix = "> " if selected else "  "
            lines.append(f"{prefix}{number}. {text}")
        return "\n".join(lines)
    
    def set_selected(self, index: int) -> None:
        """
        Set selected menu item.
        
        Args:
            index: Index of item to select
        """
        # TODO: Add bounds checking for index
        # TODO: Implement smooth selection transitions
        if 0 <= index < len(self.items):
            self.selected_index = index
            self.update(self._generate_menu_text())
