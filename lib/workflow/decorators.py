import functools
import json
import os
import sys

from lib.ide_service import IDEService


def check_config(configs: list[str], is_global: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config_file = ".workflow_config.json"
            if is_global:
                config_path = os.path.join(os.path.expanduser("~/.chat"), config_file)
            else:
                config_path = os.path.join(os.getcwd(), ".chat", config_file)

            if not os.path.exists(config_path):
                return func(False, *args, **kwargs)

            with open(config_path, "r") as f:
                config = json.load(f)

            for config_name in configs:
                if config_name not in config:
                    return func(False, *args, **kwargs)

            return func(True, *args, **kwargs)

        return wrapper

    return decorator


def check_select_code(description: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            selected_data = IDEService().get_selected_range().dict()
            if (
                selected_data["range"]["start"]["line"] == -1
                or selected_data["range"]["start"] == selected_data["range"]["end"]
            ):
                print(description, file=sys.stderr)
                sys.exit(1)
            return func(selected_data, *args, **kwargs)

        return wrapper

    return decorator


def check_input(description: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg = sys.argv[1]
            if len(arg) == 0:
                print(description, file=sys.stderr)
                sys.exit(1)
            return func(arg, *args, **kwargs)

        return wrapper

    return decorator
