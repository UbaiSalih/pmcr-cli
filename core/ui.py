# core/ui.py

"""
This module centralizes *all* terminal interaction for the application.

The main goal is to keep a strict separation between:
- Business logic (runner, loader, config, etc.)
- CLI presentation and formatting

By isolating terminal output here, we can:
- Change colors, styles or wording consistently
- Replace Rich with another UI library if needed
- Redesign the CLI look & feel without touching the core logic

If someone wants to:
- Swap Rich for a different library
- Redesign the CLI output
- Add timestamps, log levels or structured logs

This should be the *only* file that needs to be modified.
"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn


class UI:
    """
    Responsible for all visual output of the CLI.

    This class acts as an abstraction layer between:
    - The application core
    - The Rich library

    The rest of the codebase should never print directly
    to stdout or stderr — all output goes through this class.
    """

    def __init__(self):
        """
        Initialize the Rich console.

        A single Console instance is created and reused
        for the entire lifetime of the application.

        This provides:
        - Consistent output formatting
        - Centralized control over styles
        - An easy path for future extensions (file logging, redirection, etc.)
        """
        self.console = Console()

    def header(self, title):
        """
        Render a visual section header.

        Typically used at the beginning of a command execution
        to clearly indicate what is about to run.

        Args:
            title (str): Text displayed as the section header.
        """
        self.console.rule(f"[bold blue]{title}")

    def info(self, msg):
        """
        Display an informational message.

        Intended for:
        - Regular log messages
        - Non-critical status updates
        - Progress-related information that does not require a progress bar

        Args:
            msg (str): Message to display.
        """
        self.console.print(f"[cyan][INFO][/cyan] {msg}")

    def error(self, msg):
        """
        Display a recoverable error message.

        Used when:
        - A command fails
        - An operation cannot continue
        but the application itself is still in a valid state.

        Args:
            msg (str): Error message.
        """
        self.console.print(f"[red][ERROR][/red] {msg}")

    def fatal(self, msg):
        """
        Display a fatal error message.

        Used when:
        - The application cannot continue execution
        - A critical configuration is missing or invalid
        - The system is in an unrecoverable state

        This is usually followed by a sys.exit().
        """
        self.console.print(f"[bold red][FATAL][/bold red] {msg}")

    def success(self, msg):
        """
        Display a success message.

        Used to clearly signal that:
        - A command completed successfully
        - The execution flow reached a clean end state

        Args:
            msg (str): Success message.
        """
        self.console.print(f"[green][DONE][/green] {msg}")

    def progress(self, description):
        """
        Create and return a progress context.

        This method does NOT start the progress bar automatically.
        Instead, it returns a Progress instance meant to be used
        as a context manager.

        Typical usage:

            with ui.progress("Executing command") as progress:
                task = progress.add_task("Working...", total=100)
                progress.update(task, completed=50)

        This approach allows:
        - Real progress bars
        - Animated spinners
        - Clear percentage feedback
        - Continuous user feedback during long operations

        Args:
            description (str): High-level description of the process.

        Returns:
            rich.progress.Progress
        """
        return Progress(
            # Animated spinner shown while the task is active
            SpinnerColumn(),

            # Descriptive text for the current task
            TextColumn("[progress.description]{task.description}"),

            # Visual progress bar
            BarColumn(),

            # Numeric percentage indicator
            TextColumn("{task.percentage:>3.0f}%"),

            # Reuse the main console instance
            console=self.console,
        )