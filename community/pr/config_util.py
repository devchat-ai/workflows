import json
import os

import yaml

from lib.chatmark import Radio, TextEditor


def _parse_pr_host(pr_url):
    fields = pr_url.split("/")
    for field in fields:
        if field.find(".") > 0:
            return field
    return pr_url


def _read_config_value(key):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if key in config_data:
                return config_data[key]
    return None


def _save_config_value(key, value):
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")

    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    config_data[key] = value
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


# 根据PR URL获取不同的仓库管理类型
# 支持的类型有：github gitlab bitbucket bitbucket_server azure codecommit gerrit
def get_repo_type(url):
    # 根据URL的特征判断仓库管理类型
    if "github.com" in url:
        return "github"
    elif "gitlab.com" in url or "gitlab" in url:
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
        pr_host = _parse_pr_host(url)
        repo_type_map = _read_config_value("repo_type_map")
        if repo_type_map and pr_host in repo_type_map:
            return repo_type_map[pr_host]
        if not repo_type_map:
            repo_type_map = {}

        radio = Radio(
            ["github", "gitlab", "bitbucket", "bitbucket_server", "azure", "codecommit", "gerrit"],
            title="Choose the type of your repo:",
        )
        radio.render()
        if radio.selection is None:
            return None

        rtype = [
            "github",
            "gitlab",
            "bitbucket",
            "bitbucket_server",
            "azure",
            "codecommit",
            "gerrit",
        ][radio.selection]
        repo_type_map[pr_host] = rtype
        _save_config_value("repo_type_map", repo_type_map)
        return rtype


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


def read_review_inline_config():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "pr_review_inline" in config_data:
                return config_data["pr_review_inline"]
    return False


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

    pr_host = _parse_pr_host(pr_url)
    if repo_type == "gitlab":
        # get gitlab host
        gitlab_host_map = _read_config_value("gitlab_host_map")
        if gitlab_host_map and pr_host in gitlab_host_map:
            repo_type = gitlab_host_map[pr_host]
        else:
            if not gitlab_host_map:
                gitlab_host_map = {}
            gitlab_host_editor = TextEditor(
                "", "Please input your gitlab host(for example: https://www.gitlab.com):"
            )
            gitlab_host_editor.render()
            gitlab_host = gitlab_host_editor.new_text
            if not gitlab_host:
                return ""
            gitlab_host_map[pr_host] = gitlab_host
            _save_config_value("gitlab_host_map", gitlab_host_map)
            repo_type = gitlab_host

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


def get_gitlab_host(pr_url):
    pr_host = _parse_pr_host(pr_url)
    gitlab_host_map = _read_config_value("gitlab_host_map")
    if gitlab_host_map and pr_host in gitlab_host_map:
        return gitlab_host_map[pr_host]
    if not gitlab_host_map:
        gitlab_host_map = {}

    gitlab_host_editor = TextEditor(
        "https://www.gitlab.com",
        "Please input your gitlab host(for example: https://www.gitlab.com):",
    )
    gitlab_host_editor.render()
    host = gitlab_host_editor.new_text
    if host:
        gitlab_host_map[pr_host] = host
        _save_config_value("gitlab_host_map", gitlab_host_map)
    return host


def get_model_max_input(model):
    config_file = os.path.expanduser("~/.chat/config.yml")
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            yaml_contents = file.read()
            parsed_yaml = yaml.safe_load(yaml_contents)
            for model_t in parsed_yaml.get("models", {}):
                if model_t == model:
                    return parsed_yaml["models"][model_t].get("max_input_tokens", 6000)
        return 6000
    except Exception:
        return 6000
