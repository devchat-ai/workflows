import json
import os
import sys

from lib.chatmark import Checkbox

# Configuration items
CONFIG_ITEMS = {
    "pr_review_inline": "PR Review Inline Enabled",
}

# Configuration file paths
GLOBAL_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".chat", ".workflow_config.json")


def read_config(config_path, item):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get(item)
    return None


def save_config(config_path, item, value):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}

    config[item] = value
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def is_pre_review_inline_enabled(current_value=False):
    print("\n\nEnable PR Review Inline:\n\n")
    checkbox = Checkbox(
        [
            "PR Review Inline Enabled",
        ],
        [current_value],
    )
    checkbox.render()

    print(f"\n\ncheckbox.selections: {checkbox.selections}\n\n")
    if len(checkbox.selections) > 0:
        return True
    if checkbox.selections is None:
        return None
    return False


def main():
    print("Starting configuration of workflow settings...", end="\n\n", flush=True)
    print(
        "If you want to change access token or host url, "
        "please edit the configuration file directly."
    )
    print("Configuration file is located at:", GLOBAL_CONFIG_PATH, end="\n\n", flush=True)

    pr_review_inline_enable = read_config(GLOBAL_CONFIG_PATH, "pr_review_inline")

    pr_review_inline_enable = is_pre_review_inline_enabled(pr_review_inline_enable or False)
    if pr_review_inline_enable is not None:
        save_config(GLOBAL_CONFIG_PATH, "pr_review_inline", pr_review_inline_enable)
    print("Workflow settings configuration successful.")
    sys.exit(0)


if __name__ == "__main__":
    main()
