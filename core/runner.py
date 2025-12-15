import time
import traceback
from core.loader import load_callable

# Ejecuta un comando definido en el cfg
def run_command(config, name, args, ui):
    commands = config["modules"]

    if name not in commands:
        raise RuntimeError(f"Command '{name}' not defined")

    target = commands[name]
    path, func = target.split(":")

    ui.header(f"Running command: {name}")
    ui.info(f"Loading {path}:{func}")

    callable_fn = load_callable(path, func)

    start = time.time()

    try:
        with ui.progress("Executing command") as progress:
            task = progress.add_task("Working...", total=100)

            # Contexto mínimo para el comando
            ctx = {
                "progress": lambda p: progress.update(task, completed=p),
                "log": ui.info,
            }

            callable_fn(args, ctx)

    except Exception as e:
        ui.error("Command failed")
        ui.console.print(traceback.format_exc())
        raise

    elapsed = time.time() - start
    ui.success(f"Completed in {elapsed:.2f}s")
