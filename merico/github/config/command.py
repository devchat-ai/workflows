import sys
import json
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common_util import editor  # noqa: E402


def read_issue_url():
    config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "issue_repo" in config_data:
                return config_data["issue_repo"]
    return ""

def save_issue_url(issue_url):
    config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    # make dirs
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    
    config_data["issue_repo"] = issue_url
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

def read_github_token():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "github_token" in config_data:
                return config_data["github_token"]
    return ""

def save_github_token(github_token):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    
    config_data["github_token"] = github_token
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


@editor("Please specify the issue's repository, "
        "If the issue is within this repository, no need to specify. "
        "Otherwise, format as: username/repository-name")
@editor("Input your github TOKEN to access github api:")
def edit_issue(issue_url, github_token):
    pass


def main():
    print("start config git settings ...", end="\n\n", flush=True)

    issue_url = read_issue_url()
    github_token = read_github_token()

    issue_url, github_token = edit_issue(issue_url, github_token)
    if issue_url:
        save_issue_url(issue_url)
    if github_token:
        save_github_token(github_token)
    else:
        print("Please specify the github token to access github api.")
        sys.exit(0)

    print("config git settings successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
