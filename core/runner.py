# core/runner.py

"""
This module is responsible for executing a command defined in the configuration.

Its main responsibilities are:
- Resolving which command the user requested
- Dynamically loading the associated callable
- Preparing the execution context
- Coordinating the user interface (UI)
- Capturing execution time and handling errors

This file deliberately contains **no business logic** for any command.
It acts purely as an execution orchestrator.
"""

import time
import traceback

from core.loader import load_callable


def run_command(config, name, args, ui):
    """
    Execute a command defined in `modules_config.cfg`.

    High-level execution flow:
    1. Validate that the command exists
    2. Resolve the target module and function
    3. Display initial information in the UI
    4. Dynamically load the callable
    5. Execute it with arguments and an execution context
    6. Handle errors and measure execution time

    Args:
        config (dict):
            Full application configuration.
            Expected to contain:
              - config["app"]     → CLI metadata
              - config["modules"] → command definitions
        name (str):
            Name of the command requested by the user.
        args (list[str]):
            Raw command-line arguments.
        ui (UI):
            UI instance responsible for all terminal output.
    """

    # Extract relevant configuration sections
    modules = config["modules"]
    app = config["app"]

    # Early validation: the command must be defined
    if name not in modules:
        raise RuntimeError(f"Command '{name}' not defined")

    # Resolve the module definition
    module = modules[name]
    path = module["path"]
    func = module["function"]

    # Visual header for the command execution
    # Example: PMCR · backup
    ui.header(f"{app['name']} · {name}")
    ui.info(f"Loading {path}:{func}")

    # Dynamically load the callable associated with the command
    callable_fn = load_callable(path, func)

    # Capture start time for execution metrics
    start = time.time()

    try:
        # Initialize a visual progress context
        # The command is free to update it as needed
        with ui.progress("Executing command") as progress:

            # Define a task with an abstract total of 100 units
            # The command can interpret this as a percentage or milestone scale
            task = progress.add_task("Working...", total=100)

            # Execution context passed down to the command
            # This is a key mechanism to keep the core decoupled from modules
            ctx = {
                # Allows the command to update the progress bar
                # Example usage from a module:
                #   ctx
                "progress": lambda p: progress.update(task, completed=p),

                # Standardized logging entry point
                # Ensures consistent formatting and output
                "log": ui.info,
            }

            # Execute the module function
            # Expected contract:
            #   main(args: list[str], ctx: dict)
            callable_fn(args, ctx)

    except Exception:
        # On failure:
        # - Notify the user with a high-level error message
        # - Print the full traceback for debugging purposes
        ui.error("Command failed")
        ui.console.print(traceback.format_exc())

        # Re-raise the exception so the caller can decide how to handle it
        raise

    # Compute total execution time
    elapsed = time.time() - start

    # Final success message
    ui.success(f"Completed in {elapsed:.2f}s")