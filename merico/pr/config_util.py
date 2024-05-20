import json
import os

from lib.chatmark import TextEditor


# 根据PR URL获取不同的仓库管理类型
# 支持的类型有：github gitlab bitbucket bitbucket_server azure codecommit gerrit
def get_repo_type(url):
    # 根据URL的特征判断仓库管理类型
    if "github.com" in url:
        return "github"
    elif "gitlab.com" in url or "/gitlab/" in url:
        return "gitlab"
    elif "bitbucket.org" in url:
        return "bitbucket"
    elif "bitbucket-server" in url:
        return "bitbucket_server"
    elif "dev.azure.com" in url or "visualstudio.com" in url:
        return "azure"
    elif "codecommit" in url:
        return "codecommit"
    elif "gerrit" in url:
        return "gerrit"
    else:
        return ""


def read_github_token():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "github_token" in config_data:
                return config_data["github_token"]
    return ""


def read_server_access_token(repo_type):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if repo_type in config_data and "access_token" in config_data[repo_type]:
                return config_data[repo_type]["access_token"]
    return ""


def read_gitlab_host():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "gitlab_host" in config_data:
                return config_data["gitlab_host"]
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


def save_gitlab_host(github_token):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    config_data["gitlab_host"] = github_token
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def save_server_access_token(repo_type, access_token):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    if repo_type not in config_data:
        config_data[repo_type] = {}
    config_data[repo_type]["access_token"] = access_token
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def read_github_token_with_input():
    github_token = read_github_token()
    if not github_token:
        # Input your github TOKEN to access github api:
        github_token_editor = TextEditor("", "Please input your github TOKEN to access:")
        github_token = github_token_editor.new_text
        if not github_token:
            return github_token
        save_github_token(github_token)
    return github_token


def read_server_access_token_with_input(pr_url):
    repo_type = get_repo_type(pr_url)
    if not repo_type:
        return ""

    server_access_token = read_server_access_token(repo_type)
    if not server_access_token:
        # Input your server access TOKEN to access server api:
        server_access_token_editor = TextEditor(
            "", f"Please input your {repo_type} access TOKEN to access:"
        )
        server_access_token_editor.render()

        server_access_token = server_access_token_editor.new_text
        if not server_access_token:
            return server_access_token
        save_server_access_token(repo_type, server_access_token)
    return server_access_token


def gitlab_host():
    host = read_gitlab_host()
    if host:
        return host

    gitlab_host_editor = TextEditor(
        "", "Please input your gitlab host(for example: https://www.gitlab.com):"
    )
    gitlab_host_editor.render()
    host = gitlab_host_editor.new_text
    if host:
        save_gitlab_host(host)
    return host
