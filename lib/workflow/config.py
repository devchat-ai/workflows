import json
import os


def get_config_path(is_global: bool = False):
    if is_global:
        return os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    else:
        return os.path.join(os.getcwd(), ".chat", ".workflow_config.json")


def read_config(key: str, is_global: bool = False, default: str = ""):
    config_path = get_config_path(is_global)

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    return config_data.get(key) or default


def save_config(key: str, value: str, is_global: bool = False):
    config_path = get_config_path(is_global)

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    config_data[key] = value
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
