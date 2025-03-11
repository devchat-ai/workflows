import json
import os

from lib.chatmark import TextEditor


def read_custom_suggestions():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "custom_suggestions" in config_data:
                return config_data["custom_suggestions"]
    return ""


def save_custom_suggestions(custom_suggestions):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    config_data["custom_suggestions"] = custom_suggestions
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def config_custom_suggestions_with():
    custom_suggestions = read_custom_suggestions()
    if not custom_suggestions:
        custom_suggestions = "- make sure the code is efficient\n"

    # Input your github TOKEN to access github api:
    custom_suggestions_editor = TextEditor(
        custom_suggestions, "Please input your custom suggestions:"
    )
    custom_suggestions_editor.render()

    custom_suggestions = custom_suggestions_editor.new_text
    if not custom_suggestions:
        return

    save_custom_suggestions(custom_suggestions)


if __name__ == "__main__":
    config_custom_suggestions_with()
