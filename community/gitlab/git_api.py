import json
import os
import re
import subprocess
import sys
import time

import requests

from lib.chatmark import TextEditor
from lib.ide_service import IDEService


def read_gitlab_token():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "gitlab_token" in config_data:
                return config_data["gitlab_token"]

    # ask user to input gitlab token
    server_access_token_editor = TextEditor("", "Please input your GitLab access TOKEN to access:")
    server_access_token_editor.render()

    server_access_token = server_access_token_editor.new_text
    if not server_access_token:
        print("Please input your GitLab access TOKEN to continue.")
        sys.exit(-1)
    return server_access_token


current_repo_dir = None


def get_current_repo():
    """
    获取当前文件所在的仓库信息
    """
    global current_repo_dir

    if not current_repo_dir:
        selected_data = IDEService().get_selected_range().dict()
        current_file = selected_data.get("abspath", None)
        if not current_file:
            return None
        current_dir = os.path.dirname(current_file)
        try:
            # 获取仓库根目录
            current_repo_dir = (
                subprocess.check_output(
                    ["git", "rev-parse", "--show-toplevel"],
                    stderr=subprocess.DEVNULL,
                    cwd=current_dir,
                )
                .decode("utf-8")
                .strip()
            )
        except subprocess.CalledProcessError:
            # 如果发生错误，可能不在git仓库中
            return None
    return current_repo_dir


def subprocess_check_output(*popenargs, timeout=None, **kwargs):
    # 将 current_dir 添加到 kwargs 中的 cwd 参数
    current_repo = get_current_repo()
    if current_repo:
        kwargs["cwd"] = kwargs.get("cwd", current_repo)

    # 调用 subprocess.check_output
    return subprocess.check_output(*popenargs, timeout=timeout, **kwargs)


def subprocess_run(
    *popenargs, input=None, capture_output=False, timeout=None, check=False, **kwargs
):
    current_repo = get_current_repo()
    if current_repo:
        kwargs["cwd"] = kwargs.get("cwd", current_repo)

    # 调用 subprocess.run
    return subprocess.run(
        *popenargs,
        input=input,
        capture_output=capture_output,
        timeout=timeout,
        check=check,
        **kwargs,
    )


def subprocess_call(*popenargs, timeout=None, **kwargs):
    current_repo = get_current_repo()
    if current_repo:
        kwargs["cwd"] = kwargs.get("cwd", current_repo)

    # 调用 subprocess.call
    return subprocess.call(*popenargs, timeout=timeout, **kwargs)


def subprocess_check_call(*popenargs, timeout=None, **kwargs):
    current_repo = get_current_repo()
    if current_repo:
        kwargs["cwd"] = kwargs.get("cwd", current_repo)

    # 调用 subprocess.check_call
    return subprocess.check_call(*popenargs, timeout=timeout, **kwargs)


GITLAB_ACCESS_TOKEN = read_gitlab_token()
GITLAB_API_URL = "https://gitlab.com/api/v4"


def create_issue(title, description):
    headers = {
        "Private-Token": GITLAB_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "title": title,
        "description": description,
    }
    project_id = get_gitlab_project_id()
    issue_api_url = f"{GITLAB_API_URL}/projects/{project_id}/issues"
    response = requests.post(issue_api_url, headers=headers, json=data)

    if response.status_code == 201:
        print("Issue created successfully!")
        return response.json()
    else:
        print(f"Failed to create issue: {response.content}", file=sys.stderr, end="\n\n")
        return None


def update_issue_body(issue_iid, issue_body):
    headers = {
        "Private-Token": GITLAB_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "description": issue_body,
    }

    project_id = get_gitlab_project_id()
    api_url = f"{GITLAB_API_URL}/projects/{project_id}/issues/{issue_iid}"
    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 200:
        print("Issue updated successfully!")
        return response.json()
    else:
        print(f"Failed to update issue: {response.status_code}")
        return None


def get_gitlab_project_id():
    try:
        result = subprocess_check_output(
            ["git", "remote", "get-url", "origin"], stderr=subprocess.STDOUT
        ).strip()
        repo_url = result.decode("utf-8")
        print(f"Original repo URL: {repo_url}", file=sys.stderr)

        if repo_url.startswith("git@"):
            # Handle SSH URL format
            parts = repo_url.split(":")
            project_path = parts[1].replace(".git", "")
        elif repo_url.startswith("https://"):
            # Handle HTTPS URL format
            parts = repo_url.split("/")
            project_path = "/".join(parts[3:]).replace(".git", "")
        else:
            raise ValueError(f"Unsupported Git URL format: {repo_url}")

        print(f"Extracted project path: {project_path}", file=sys.stderr)
        encoded_project_path = requests.utils.quote(project_path, safe="")
        print(f"Encoded project path: {encoded_project_path}", file=sys.stderr)
        return encoded_project_path
    except subprocess.CalledProcessError as e:
        print(f"Error executing git command: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error in get_gitlab_project_id: {e}", file=sys.stderr)
        return None


# parse sub tasks in issue description
def parse_sub_tasks(description):
    sub_tasks = []
    lines = description.split("\n")
    for line in lines:
        if line.startswith("- ["):
            sub_tasks.append(line[2:])
    return sub_tasks


def update_sub_tasks(description, tasks):
    # remove all existing tasks
    lines = description.split("\n")
    updated_body = "\n".join(line for line in lines if not line.startswith("- ["))

    # add new tasks
    updated_body += "\n" + "\n".join(f"- {task}" for task in tasks)

    return updated_body


def update_task_issue_url(description, task, issue_url):
    # task is like:
    # [ ] task name
    # [x] task name
    # replace task name with issue url, like:
    # [ ] [task name](url)
    # [x] [task name](url)
    if task.find("] ") == -1:
        return None
    task = task[task.find("] ") + 2 :]
    return description.replace(task, f"[{task}]({issue_url})")


def check_git_installed():
    """
    Check if Git is installed on the local machine.

    Tries to execute 'git --version' command to determine the presence of Git.

    Returns:
        bool: True if Git is installed, False otherwise.
    """
    try:
        subprocess_run(
            ["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        print("Git is not installed on your system.")
        return False


def create_and_checkout_branch(branch_name):
    subprocess_run(["git", "checkout", "-b", branch_name], check=True)


def is_issue_url(task):
    task = task.strip()

    # 使用正则表达式匹配 http 或 https 开头，issues/数字 结尾的 URL
    pattern = r"^(http|https)://.*?/issues/\d+$"

    is_issue = bool(re.match(pattern, task))

    # print(f"Task to check: {task}", file=sys.stderr)
    # print(f"Is issue URL: {is_issue}", file=sys.stderr)

    return is_issue


def read_issue_by_url(issue_url):
    # Extract the issue number and project path from the URL
    issue_url = issue_url.replace("/-/", "/")
    parts = issue_url.split("/")
    issue_number = parts[-1]
    project_path = "/".join(
        parts[3:-2]
    )  # Assumes URL format: https://gitlab.com/project/path/-/issues/number

    # URL encode the project path
    encoded_project_path = requests.utils.quote(project_path, safe="")

    # Construct the API endpoint URL
    api_url = f"{GITLAB_API_URL}/projects/{encoded_project_path}/issues/{issue_number}"

    # Send a GET request to the API endpoint
    headers = {
        "Private-Token": GITLAB_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching issue: {response.status_code}", file=sys.stderr)
        print(f"Response content: {response.text}", file=sys.stderr)
        return None


def get_gitlab_issue_repo(issue_repo=False):
    try:
        config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
        if os.path.exists(config_path) and issue_repo:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

                if "git_issue_repo" in config_data:
                    issue_repo = requests.utils.quote(config_data["git_issue_repo"], safe="")
                    print(
                        "current issue repo:",
                        config_data["git_issue_repo"],
                        end="\n\n",
                        file=sys.stderr,
                        flush=True,
                    )
                    return config_data["git_issue_repo"]

        return get_gitlab_project_id()
    except subprocess.CalledProcessError as e:
        print(e)
        # 如果发生错误，打印错误信息
        return None
    except FileNotFoundError:
        # 如果未找到git命令，可能是没有安装git或者不在PATH中
        print("==> File not found...")
        return None


# 获取当前分支名称
def get_current_branch():
    try:
        # 使用git命令获取当前分支名称
        result = subprocess_check_output(
            ["git", "branch", "--show-current"], stderr=subprocess.STDOUT
        ).strip()
        # 将结果从bytes转换为str
        current_branch = result.decode("utf-8")
        return current_branch
    except subprocess.CalledProcessError:
        # 如果发生错误，打印错误信息
        return None
    except FileNotFoundError:
        # 如果未找到git命令，可能是没有安装git或者不在PATH中
        return None


def get_parent_branch():
    current_branch = get_current_branch()
    if current_branch is None:
        return None
    try:
        # 使用git命令获取当前分支的父分支引用
        result = subprocess_check_output(
            ["git", "rev-parse", "--abbrev-ref", f"{current_branch}@{1}"], stderr=subprocess.STDOUT
        ).strip()
        # 将结果从bytes转换为str
        parent_branch_ref = result.decode("utf-8")
        if parent_branch_ref == current_branch:
            # 如果父分支引用和当前分支相同，说明当前分支可能是基于一个没有父分支的提交创建的
            return None
        # 使用git命令获取父分支的名称
        result = subprocess_check_output(
            ["git", "name-rev", "--name-only", "--exclude=tags/*", parent_branch_ref],
            stderr=subprocess.STDOUT,
        ).strip()
        parent_branch_name = result.decode("utf-8")
        return parent_branch_name
    except subprocess.CalledProcessError as e:
        print(e)
        # 如果发生错误，打印错误信息
        return None
    except FileNotFoundError:
        # 如果未找到git命令，可能是没有安装git或者不在PATH中
        print("==> File not found...")
        return None


def get_issue_info(issue_id):
    # 获取 GitLab 项目 ID
    project_id = get_gitlab_issue_repo()
    # 构造 GitLab API 端点 URL
    api_url = f"{GITLAB_API_URL}/projects/{project_id}/issues/{issue_id}"

    # 发送 GET 请求到 API 端点
    headers = {
        "Private-Token": GITLAB_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get issue info. Status code: {response.status_code}", file=sys.stderr)
        print(f"Response content: {response.text}", file=sys.stderr)
        return None


def get_issue_info_by_url(issue_url):
    # get issue id from issue_url
    def get_issue_id(issue_url):
        # Extract the issue id from the issue_url
        issue_id = issue_url.split("/")[-1]
        return issue_id

    return get_issue_info(get_issue_id(issue_url))


# 获取当前分支自从与base_branch分叉以来的历史提交信息
def get_commit_messages(base_branch):
    # 找到当前分支与base_branch的分叉点
    merge_base = subprocess_run(
        ["git", "merge-base", "HEAD", base_branch],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # 检查是否成功找到分叉点
    if merge_base.returncode != 0:
        raise RuntimeError(f"Error finding merge base: {merge_base.stderr.strip()}")

    # 获取分叉点的提交哈希
    merge_base_commit = merge_base.stdout.strip()

    # 获取从分叉点到当前分支的所有提交信息
    result = subprocess_run(
        ["git", "log", f"{merge_base_commit}..HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # 检查git log命令是否成功执行
    if result.returncode != 0:
        raise RuntimeError(f"Error retrieving commit messages: {result.stderr.strip()}")

    # 返回提交信息列表
    return result.stdout


# 创建PR
def create_pull_request(title, description, source_branch, target_branch, project_id):
    url = f"{GITLAB_API_URL}/projects/{project_id}/merge_requests"
    headers = {"Private-Token": GITLAB_ACCESS_TOKEN, "Content-Type": "application/json"}
    payload = {
        "title": title,
        "description": description,
        "source_branch": source_branch,
        "target_branch": target_branch,
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        response_json = response.json()
        return response_json

    print(response.text, end="\n\n", file=sys.stderr)
    return None


def get_recently_mr(project_id):
    project_id = requests.utils.quote(project_id, safe="")
    url = (
        f"{GITLAB_API_URL}/projects/{project_id}/"
        "merge_requests?state=opened&order_by=updated_at&sort=desc"
    )
    headers = {
        "Private-Token": GITLAB_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)

    branch_name = get_current_branch()

    if response.status_code == 200:
        mrs = response.json()
        for mr in mrs:
            if mr["source_branch"] == branch_name:
                return mr
        return None
    else:
        return None


def run_command_with_retries(command, retries=3, delay=5):
    for attempt in range(retries):
        try:
            subprocess_check_call(command)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying... (attempt {attempt + 1}/{retries})")
                time.sleep(delay)
            else:
                print("All retries failed.")
    return False


def update_mr(project_id, mr_iid, title, description):
    project_id = requests.utils.quote(project_id, safe="")
    url = f"{GITLAB_API_URL}/projects/{project_id}/merge_requests/{mr_iid}"
    headers = {"Private-Token": GITLAB_ACCESS_TOKEN, "Content-Type": "application/json"}
    payload = {"title": title, "description": description}
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"MR updated successfully: {response.json()['web_url']}")
        return response.json()
    else:
        print("Failed to update MR.")
        return None


def check_unpushed_commits():
    try:
        # 获取当前分支的本地提交和远程提交的差异
        result = subprocess_check_output(["git", "cherry", "-v"]).decode("utf-8").strip()
        # 如果结果不为空，说明存在未push的提交
        return bool(result)
    except subprocess.CalledProcessError as e:
        print(f"Error checking for unpushed commits: {e}")
        return True


def auto_push():
    # 获取当前分支名
    if not check_unpushed_commits():
        return True
    try:
        branch = (
            subprocess_check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .strip()
            .decode("utf-8")
        )
    except subprocess.CalledProcessError as e:
        print(f"Error getting current branch: {e}")
        return False

    # 检查当前分支是否有对应的远程分支
    remote_branch_exists = subprocess_call(["git", "ls-remote", "--exit-code", "origin", branch])

    push_command = ["git", "push", "origin", branch]
    if remote_branch_exists == 0:
        # 如果存在远程分支，则直接push提交
        return run_command_with_retries(push_command)
    else:
        # 如果不存在远程分支，则发布并push提交
        push_command.append("-u")
        return run_command_with_retries(push_command)


def get_recently_pr(repo):
    url = f"{GITLAB_API_URL}/repos/{repo}/pulls?state=open&sort=updated"
    headers = {
        "Authorization": f"token {GITLAB_ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)

    branch_name = get_current_branch()

    if response.status_code == 200:
        prs = response.json()
        for pr in prs:
            if pr["head"]["ref"] == branch_name:
                return pr
        return None
    else:
        return None


def update_pr(pr_number, title, description, repo_name):
    url = f"{GITLAB_API_URL}/repos/{repo_name}/pulls/{pr_number}"
    headers = {"Authorization": f"token {GITLAB_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"title": title, "description": description}
    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print(f"PR updated successfully: {response.json()['web_url']}")
        return response.json()
    else:
        print("Failed to update PR.")
        return None


def get_last_base_branch(default_branch):
    """read last base branch from config file"""

    def read_config_item(config_path, item):
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get(item)
        return None

    project_config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    last_base_branch = read_config_item(project_config_path, "last_base_branch")
    if last_base_branch:
        return last_base_branch
    return default_branch


def save_last_base_branch(base_branch=None):
    """save last base branch to config file"""

    def save_config_item(config_path, item, value):
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}

        config[item] = value
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    if not base_branch:
        base_branch = get_current_branch()
    project_config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    save_config_item(project_config_path, "last_base_branch", base_branch)
