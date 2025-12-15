# core/loader.py

"""
This module is responsible for dynamically loading Python code at runtime.

It is a key piece of the project architecture:
- Allows commands to be executed without static imports
- Prevents tight coupling between the core and individual commands
- Enables command definitions to live entirely in configuration

Thanks to this module:
- New commands can be added without modifying the core
- The CLI effectively behaves as a lightweight plugin runner
"""

import importlib.util
from pathlib import Path


def load_callable(path, func_name):
    """
    Dynamically load a Python file and return a specific callable from it.

    This function performs the following steps:
    1. Receives a path to a `.py` file
    2. Loads that file as a Python module
    3. Looks up a function inside the loaded module
    4. Returns a callable reference to that function

    The function is NOT executed here — it is only resolved and returned.

    Args:
        path (str): Path to the Python file containing the command.
        func_name (str): Name of the function that acts as the entry point.

    Returns:
        callable: A reference to the requested Python function.

    Raises:
        RuntimeError:
            - If the file does not exist
            - If the module cannot be loaded
            - If the requested function is not defined in the module
    """

    # Resolve to an absolute path to avoid ambiguity
    file_path = Path(path).resolve()

    # Early validation: the file must exist
    if not file_path.exists():
        raise RuntimeError(f"Command file not found: {file_path}")

    # Create a module specification from the file path
    # This allows loading modules that are NOT part of sys.path
    spec = importlib.util.spec_from_file_location(
        file_path.stem,  # Logical module name
        file_path        # Actual file location
    )

    # Instantiate an empty module object from the spec
    module = importlib.util.module_from_spec(spec)

    # Execute the file's code within the newly created module
    # This is effectively a dynamic import
    spec.loader.exec_module(module)

    # Validate that the requested function exists in the module
    if not hasattr(module, func_name):
        raise RuntimeError(f"Function '{func_name}' not found in {file_path}")

    # Return a reference to the callable
    # The runner is responsible for invoking it
    return getattr(module, func_name)