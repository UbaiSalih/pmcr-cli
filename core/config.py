# core/config.py

"""
This module is responsible for loading, validating and normalizing
all declarative configuration used by the CLI.

Key design principles:
- The application contains no hardcoded command logic.
- All behavior is defined through `.cfg` files.
- Configuration is fully validated *before* any command is executed.

If the configuration is invalid:
→ the application does NOT proceed
→ commands are never executed in an inconsistent state

This file is the natural place to:
- Introduce new configuration options
- Support additional configuration formats
- Implement more advanced validation rules
"""

import configparser
from pathlib import Path


def _load_cfg(path: str) -> configparser.ConfigParser:
    """
    Load a `.cfg` file from disk and return a ConfigParser instance.

    This is an internal helper (note the leading underscore):
    - It does not validate semantic content
    - It only ensures the file exists and can be read

    Keeping this logic isolated allows us to:
    - Reuse the low-level loading mechanism
    - Centralize path handling and IO errors
    - Extend behavior later (encoding, includes, overrides, etc.)

    Args:
        path (str): Path to the `.cfg` file.

    Returns:
        configparser.ConfigParser
    """
    cfg_path = Path(path)

    # Early validation: the file must exist
    if not cfg_path.exists():
        raise RuntimeError(f"Configuration file not found: {path}")

    parser = configparser.ConfigParser()

    # Read the file exactly as it exists on disk
    parser.read(cfg_path)

    return parser


def load_app_config(path: str) -> dict:
    """
    Load and validate the application configuration (`cli.cfg`).

    This file defines the *identity* of the CLI, not its behavior.
    It typically contains:
    - Public CLI name
    - Version
    - Short description

    Keeping this configuration separate allows:
    - Reusing the same execution engine for multiple CLIs
    - Versioning the CLI independently of commands
    - Displaying consistent metadata across help, logs and UI

    Args:
        path (str): Path to `cli.cfg`.

    Returns:
        dict: Normalized application metadata with the following keys:
            {
                "name": str,
                "version": str,
                "description": str
            }
    """
    cfg = _load_cfg(path)

    # The [app] section is mandatory
    if "app" not in cfg:
        raise RuntimeError("Missing [app] section in cli.cfg")

    app = cfg["app"]

    # Minimum required keys to identify the CLI
    required_keys = ("name", "version", "description")
    for key in required_keys:
        # Validate presence and ensure the value is not empty
        if key not in app or not app[key].strip():
            raise RuntimeError(f"Missing or empty '{key}' in [app] section")

    # Return a plain dictionary instead of exposing ConfigParser
    # to the rest of the core
    return {
        "name": app["name"],
        "version": app["version"],
        "description": app["description"],
    }


def load_modules_config(path: str) -> dict:
    """
    Load and validate the modules configuration (`modules_config.cfg`).

    This file defines:
    - Which commands exist
    - Which Python file implements each command
    - Which function acts as the entry point

    Each entry follows the format:
        command_name = path/to/file.py:function_name

    Example:
        hello = modules/hello.py:main

    Args:
        path (str): Path to `modules_config.cfg`.

    Returns:
        dict: Normalized module definitions in the form:
            {
                "command": {
                    "path": "modules/hello.py",
                    "function": "main"
                }
            }
    """
    cfg = _load_cfg(path)

    # The [modules] section is mandatory
    if "modules" not in cfg:
        raise RuntimeError("Missing [modules] section in modules_config.cfg")

    modules = cfg["modules"]

    # At least one command must be defined
    if not modules:
        raise RuntimeError("No modules defined in modules_config.cfg")

    parsed_modules = {}

    # Process each command definition from the config
    for name, target in modules.items():

        # Basic format validation
        if ":" not in target:
            raise RuntimeError(
                f"Invalid module definition for '{name}'. "
                "Expected format: path/to/file.py:function"
            )

        path_part, func_part = target.split(":", 1)

        # Semantic validation
        if not path_part or not func_part:
            raise RuntimeError(
                f"Invalid module definition for '{name}'. "
                "Path and function must be non-empty"
            )

        # Store the normalized command definition
        parsed_modules[name] = {
            "path": path_part,
            "function": func_part,
        }

    return parsed_modules


def load_config(app_cfg_path: str, modules_cfg_path: str) -> dict:
    """
    Load the complete application configuration.

    This function acts as the single entry point
    for configuration loading within the core.

    Execution flow:
    1. Load and validate `cli.cfg`
    2. Load and validate `modules_config.cfg`
    3. Combine both into a single coherent structure

    If any step fails:
    → an exception is raised
    → the application does NOT continue execution

    Args:
        app_cfg_path (str): Path to `cli.cfg`.
        modules_cfg_path (str): Path to `modules_config.cfg`.

    Returns:
        dict: Fully validated configuration structure:
            {
                "app": {...},
                "modules": {...}
            }
    """
    app_config = load_app_config(app_cfg_path)
    modules_config = load_modules_config(modules_cfg_path)

    return {
        "app": app_config,
        "modules": modules_config,
    }