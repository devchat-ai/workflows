import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from common_util import assert_exit, ui_edit  # noqa: E402
from devchat.llm import (  # noqa: E402
    chat_json,
)
from git_api import (  # noqa: E402
    auto_push,
    get_commit_messages,
    get_current_branch,
    get_github_repo,
    get_issue_info,
    get_last_base_branch,
    get_recently_pr,
    save_last_base_branch,
    update_pr,
)


# 从分支名称中提取issue id
def extract_issue_id(branch_name):
    if "#" in branch_name:
        return branch_name.split("#")[-1]
    return None


# 使用LLM模型生成PR内容
PROMPT = (
    "Create a pull request title and body based on "
    "the following issue and commit messages, if there is an "
    "issue, close that issue in PR body as <user>/<repo>#issue_id:\n"
    "Issue: {issue}\n"
    "Commits:\n{commit_messages}\n"
    "The response result should format as JSON object as following:\n"
    '{{"title": "pr title", "body": "pr body"}}'
)


@chat_json(prompt=PROMPT)
def generate_pr_content_llm(issue, commit_messages):
    pass


def generate_pr_content(issue, commit_messages):
    response = generate_pr_content_llm(issue=json.dumps(issue), commit_messages=commit_messages)
    assert_exit(not response, "Failed to generate PR content.", exit_code=-1)
    return response.get("title"), response.get("body")


@ui_edit(ui_type="editor", description="Edit PR title:")
@ui_edit(ui_type="editor", description="Edit PR body:")
def edit_pr(title, body):
    pass


@ui_edit(ui_type="editor", description="Edit base branch:")
def edit_base_branch(base_branch):
    pass


def get_issue_json(issue_id):
    issue = {"id": "no issue id", "title": "", "body": ""}
    if issue_id:
        issue = get_issue_info(issue_id)
        assert_exit(not issue, "Failed to retrieve issue with ID: {issue_id}", exit_code=-1)
        issue = {
            "id": issue_id,
            "html_url": issue["html_url"],
            "title": issue["title"],
            "body": issue["body"],
        }
    return issue


# 主函数
def main():
    print("start update_pr ...", end="\n\n", flush=True)

    base_branch = get_last_base_branch("main")
    base_branch = edit_base_branch(base_branch)
    if isinstance(base_branch, list) and len(base_branch) > 0:
        base_branch = base_branch[0]
        save_last_base_branch(base_branch)

    repo_name = get_github_repo()
    branch_name = get_current_branch()
    issue_id = extract_issue_id(branch_name)

    # print basic info, repo_name, branch_name, issue_id
    print("repo name:", repo_name, end="\n\n")
    print("branch name:", branch_name, end="\n\n")
    print("issue id:", issue_id, end="\n\n")

    issue = get_issue_json(issue_id)
    commit_messages = get_commit_messages(base_branch)

    recent_pr = get_recently_pr(repo_name)
    assert_exit(not recent_pr, "Failed to get recent PR.", exit_code=-1)

    print("generating pr title and body ...", end="\n\n", flush=True)
    pr_title, pr_body = generate_pr_content(issue, commit_messages)
    assert_exit(not pr_title, "Failed to generate PR content.", exit_code=-1)

    pr_title, pr_body = edit_pr(pr_title, pr_body)
    assert_exit(not pr_title, "PR creation cancelled.", exit_code=0)

    is_push_success = auto_push()
    assert_exit(not is_push_success, "Failed to push changes.", exit_code=-1)

    pr = update_pr(recent_pr["number"], pr_title, pr_body, repo_name)
    assert_exit(not pr, "Failed to update PR.", exit_code=-1)

    print(f"PR updated successfully: {pr['html_url']}")


if __name__ == "__main__":
    main()
