import json
import os
import subprocess
import sys
import time

import requests

from lib.chatmark import TextEditor


def read_github_token():
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            if "github_token" in config_data:
                return config_data["github_token"]

    # ask user to input github token
    server_access_token_editor = TextEditor("", "Please input your GITHUB access TOKEN to access:")
    server_access_token_editor.render()

    server_access_token = server_access_token_editor.new_text
    if not server_access_token:
        print("Please input your GITHUB access TOKEN to continue.")
        sys.exit(-1)
    return server_access_token


GITHUB_ACCESS_TOKEN = read_github_token()
GITHUB_API_URL = "https://api.github.com"


def create_issue(title, body):
    headers = {
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": title,
        "body": body,
    }
    issue_api_url = f"https://api.github.com/repos/{get_github_repo(True)}/issues"
    response = requests.post(issue_api_url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print("Issue created successfully!")
        return response.json()
    else:
        print(f"Failed to create issue: {response.content}", file=sys.stderr, end="\n\n")
        return None


def update_issue_body(issue_url, issue_body):
    """
    Update the body text of a GitHub issue.

    :param issue_url: The API URL of the issue to update.
    :param issue_body: The new body text for the issue.
    """
    headers = {
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "body": issue_body,
    }

    issue_api_url = f"https://api.github.com/repos/{get_github_repo(True)}/issues"
    api_url = f"{issue_api_url}/{issue_url.split('/')[-1]}"
    response = requests.patch(api_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Issue updated successfully!")
        return response.json()
    else:
        print(f"Failed to update issue: {response.status_code}")
        return None


# parse sub tasks in issue body
def parse_sub_tasks(body):
    sub_tasks = []
    lines = body.split("\n")
    for line in lines:
        if line.startswith("- ["):
            sub_tasks.append(line[2:])
    return sub_tasks


def update_sub_tasks(body, tasks):
    # remove all existing tasks
    lines = body.split("\n")
    updated_body = "\n".join(line for line in lines if not line.startswith("- ["))

    # add new tasks
    updated_body += "\n" + "\n".join(f"- {task}" for task in tasks)

    return updated_body


def update_task_issue_url(body, task, issue_url):
    # task is like:
    # [ ] task name
    # [x] task name
    # replace task name with issue url, like:
    # [ ] [task name](url)
    # [x] [task name](url)
    if task.find("] ") == -1:
        return None
    task = task[task.find("] ") + 2 :]
    return body.replace(task, f"[{task}]({issue_url})")


def check_git_installed():
    """
    Check if Git is installed on the local machine.

    Tries to execute 'git --version' command to determine the presence of Git.

    Returns:
        bool: True if Git is installed, False otherwise.
    """
    try:
        subprocess.run(
            ["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        print("Git is not installed on your system.")
        return False


def create_and_checkout_branch(branch_name):
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)


def is_issue_url(task):
    issue_url = f"https://github.com/{get_github_repo(True)}/issues"
    return task.strip().startswith(issue_url)


def read_issue_by_url(issue_url):
    issue_number = issue_url.split("/")[-1]

    # Construct the API endpoint URL
    issue_api_url = f"https://api.github.com/repos/{get_github_repo(True)}/issues"
    api_url = f"{issue_api_url}/{issue_number}"

    # Send a GET request to the API endpoint
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}",
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_github_repo(issue_repo=False):
    try:
        config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
        if os.path.exists(config_path) and issue_repo:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                if "issue_repo" in config_data:
                    print(
                        "current issue repo:",
                        config_data["issue_repo"],
                        end="\n\n",
                        file=sys.stderr,
                        flush=True,
                    )
                    return config_data["issue_repo"]

        # 使用git命令获取当前仓库的URL
        result = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], stderr=subprocess.STDOUT
        ).strip()
        # 将结果从bytes转换为str并提取出仓库信息
        repo_url = result.decode("utf-8")
        # 假设repo_url的格式为：https://github.com/username/repo.git
        parts = repo_url.split("/")
        repo = parts[-1].replace(".git", "")
        username = parts[-2].split(":")[-1]
        github_repo = f"{username}/{repo}"
        print("current github repo:", github_repo, end="\n\n", file=sys.stderr, flush=True)
        return github_repo
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
        result = subprocess.check_output(
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
        result = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", f"{current_branch}@{1}"], stderr=subprocess.STDOUT
        ).strip()
        # 将结果从bytes转换为str
        parent_branch_ref = result.decode("utf-8")
        print("==>", parent_branch_ref)
        if parent_branch_ref == current_branch:
            # 如果父分支引用和当前分支相同，说明当前分支可能是基于一个没有父分支的提交创建的
            return None
        # 使用git命令获取父分支的名称
        result = subprocess.check_output(
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
    # Construct the API endpoint URL
    issue_api_url = f"https://api.github.com/repos/{get_github_repo(True)}/issues"
    api_url = f"{issue_api_url}/{issue_id}"

    # Send a GET request to the API endpoint
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}",
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
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
    merge_base = subprocess.run(
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
    result = subprocess.run(
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
def create_pull_request(title, body, head, base, repo_name):
    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls"
    print("url:", url, end="\n\n")
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"title": title, "body": body, "head": head, "base": base}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 201:
        return response.json()
    print(response.text, end="\n\n", file=sys.stderr)
    return None


def run_command_with_retries(command, retries=3, delay=5):
    for attempt in range(retries):
        try:
            subprocess.check_call(command)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying... (attempt {attempt + 1}/{retries})")
                time.sleep(delay)
            else:
                print("All retries failed.")
    return False


def check_unpushed_commits():
    try:
        # 获取当前分支的本地提交和远程提交的差异
        result = subprocess.check_output(["git", "cherry", "-v"]).decode("utf-8").strip()
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
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .strip()
            .decode("utf-8")
        )
    except subprocess.CalledProcessError as e:
        print(f"Error getting current branch: {e}")
        return False

    # 检查当前分支是否有对应的远程分支
    remote_branch_exists = subprocess.call(["git", "ls-remote", "--exit-code", "origin", branch])

    push_command = ["git", "push", "origin", branch]
    if remote_branch_exists == 0:
        # 如果存在远程分支，则直接push提交
        return run_command_with_retries(push_command)
    else:
        # 如果不存在远程分支，则发布并push提交
        push_command.append("-u")
        return run_command_with_retries(push_command)


def get_recently_pr(repo):
    url = f"{GITHUB_API_URL}/repos/{repo}/pulls?state=open&sort=updated"
    headers = {
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    print("=>:", url)

    branch_name = get_current_branch()

    if response.status_code == 200:
        prs = response.json()
        for pr in prs:
            if pr["head"]["ref"] == branch_name:
                return pr
        return None
    else:
        return None


def update_pr(pr_number, title, body, repo_name):
    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/{pr_number}"
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"title": title, "body": body}
    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print(f"PR updated successfully: {response.json()['html_url']}")
        return response.json()
    else:
        print("Failed to update PR.")
        return None
