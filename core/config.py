import configparser
from pathlib import Path

# Carga y valida el archivo service.cfg
def load_config(path):
    cfg_path = Path(path)

    if not cfg_path.exists():
        raise RuntimeError("Configuration file not found. Add settings.cfg to your folder.")

    parser = configparser.ConfigParser()
    parser.read(cfg_path)

    if "service" not in parser:
        raise RuntimeError("Missing [service] section")

    if "commands" not in parser:
        raise RuntimeError("Missing [commands] section")

    if not parser["commands"]:
        raise RuntimeError("No commands defined")

    return parser
