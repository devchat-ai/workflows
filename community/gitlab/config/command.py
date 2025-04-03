import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common_util import editor  # noqa: E402


def read_issue_url():
    config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "git_issue_repo" in config_data:
                return config_data["git_issue_repo"]
    return ""


def save_issue_url(issue_url):
    config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    # make dirs
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    config_data["git_issue_repo"] = issue_url
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def read_gitlab_token():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "gitlab_token" in config_data:
                return config_data["gitlab_token"]
    return ""


def save_gitlab_token(github_token):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    config_data["gitlab_token"] = github_token
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def read_gitlab_api_url():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "gitlab_api_url" in config_data:
                return config_data["gitlab_api_url"]
    return ""


def save_gitlab_api_url(gitlab_api_url):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    config_data["gitlab_api_url"] = gitlab_api_url
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


@editor(
    "Please specify the issue's repository, "
    "If the issue is within this repository, no need to specify. "
    "Otherwise, format as: username/repository-name"
)
@editor("Input your gitlab API URL to access gitlab api:")
@editor("Input your gitlab TOKEN to access gitlab api:")
def edit_issue(issue_url, gitlab_api_url, gitlab_token):
    pass


def main():
    print("start config git settings ...", end="\n\n", flush=True)

    issue_url = read_issue_url()
    gitlab_token = read_gitlab_token()
    gitlab_api_url = read_gitlab_api_url()
    issue_url, gitlab_api_url, gitlab_token = edit_issue(issue_url, gitlab_api_url, gitlab_token)
    if issue_url:
        save_issue_url(issue_url)
    if gitlab_token:
        save_gitlab_token(gitlab_token)
    if gitlab_api_url:
        save_gitlab_api_url(gitlab_api_url)
    if not gitlab_api_url:
        print("Please specify the gitlab api url to access gitlab api.")
        sys.exit(0)
    if not gitlab_token:
        print("Please specify the gitlab token to access gitlab api.")
        sys.exit(0)

    print("config gitlab settings successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
