# pmcr.py

"""
This file is the ENTRY POINT of the CLI (Command Line Interface).

It is the only file executed directly by the end user:
- python pmcr.py hello
- pmcr.exe hello

Its responsibilities are intentionally limited to:
- Initializing the user interface
- Loading and validating configuration
- Parsing command-line arguments
- Delegating execution to the runner

This file contains NO business logic.
It simply acts as the glue between the core components.
"""

import sys

from core.config import load_config
from core.runner import run_command
from core.ui import UI


def main():
    """
    Main entry point of the application.

    High-level execution flow:
    1. Initialize the UI layer
    2. Load and validate global configuration (app + modules)
    3. Validate command-line arguments
    4. Execute the requested command
    5. Handle errors in a controlled and user-friendly way
    """

    # Initialize the user interface
    # All terminal output is routed through this class
    ui = UI()

    # Load and validate configuration
    # IMPORTANT:
    # If configuration loading fails, execution must not continue.
    # This prevents inconsistent states or partial executions.
    try:
        config = load_config("cli.cfg", "modules_config.cfg")
    except Exception as e:
        ui.fatal(str(e))
        sys.exit(1)

    # Extract application metadata
    app = config["app"]
    app_name = app["name"]

    # Argument validation:
    # The first argument must be the command name
    if len(sys.argv) < 2:
        ui.error("No command specified")
        ui.info(f"Usage: {app_name} <command> [args]")
        sys.exit(1)

    # Separate the command name from its arguments
    command_name = sys.argv[1]
    command_args = sys.argv[2:]

    try:
        # Delegate execution to the runner
        # From this point on:
        # - the core resolves the module
        # - the callable is loaded dynamically
        # - the command is executed with context and UI access
        run_command(config, command_name, command_args, ui)

    except Exception as e:
        # Final catch for unhandled errors
        # Guarantees:
        # - a clear message for the user
        # - a clean and controlled shutdown
        ui.fatal(str(e))

        # On Windows, pausing allows the user to read the error
        input("Press ENTER to exit...")
        sys.exit(1)


# Allows the file to be executed directly
# while still supporting controlled imports
if __name__ == "__main__":
    main()