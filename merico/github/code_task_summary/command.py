import json
import os
import sys

from devchat.llm import chat_json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common_util import assert_exit, ui_edit  # noqa: E402
from git_api import (  # noqa: E402
    check_git_installed,
    get_current_branch,
    get_github_repo,
    get_issue_info,
    is_issue_url,
    read_issue_by_url,
)


def extract_issue_id(branch_name):
    if "#" in branch_name:
        return branch_name.split("#")[-1]
    return None


# Function to generate a random branch name
PROMPT = (
    "You are a coding engineer, required to summarize the ISSUE description into a coding task description of no more than 50 words. \n"  # noqa: E501
    "The ISSUE description is as follows: {issue_body}, please summarize the corresponding coding task description.\n"  # noqa: E501
    'The coding task description should be output in JSON format, in the form of: {{"summary": "code task summary"}}\n'  # noqa: E501
)


@chat_json(prompt=PROMPT)
def generate_code_task_summary(issue_body):
    pass


@ui_edit(ui_type="editor", description="Edit code task summary:")
def edit_code_task_summary(task_summary):
    pass


def get_issue_or_task(task):
    if is_issue_url(task):
        issue = read_issue_by_url(task.strip())
        assert_exit(not issue, "Failed to read issue.", exit_code=-1)

        return json.dumps({"id": issue["number"], "title": issue["title"], "body": issue["body"]})
    else:
        return task


def get_issue_json(issue_id, task):
    issue = {"id": "no issue id", "title": "", "body": task}
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


# Main function
def main():
    print("Start update code task summary ...", end="\n\n", flush=True)

    is_git_installed = check_git_installed()
    assert_exit(not is_git_installed, "Git is not installed.", exit_code=-1)

    task = sys.argv[1]

    repo_name = get_github_repo()
    branch_name = get_current_branch()
    issue_id = extract_issue_id(branch_name)

    # print basic info, repo_name, branch_name, issue_id
    print("repo name:", repo_name, end="\n\n")
    print("branch name:", branch_name, end="\n\n")
    print("issue id:", issue_id, end="\n\n")

    issue = get_issue_json(issue_id, task)
    assert_exit(not issue["body"], "Failed to retrieve issue with ID: {issue_id}", exit_code=-1)

    # Generate 5 branch names
    print("Generating code task summary ...", end="\n\n", flush=True)
    code_task_summary = generate_code_task_summary(issue_body=issue["body"])
    assert_exit(not code_task_summary, "Failed to generate code task summary.", exit_code=-1)
    assert_exit(
        not code_task_summary.get("summary", None),
        "Failed to generate code task summary, missing summary field in result.",
        exit_code=-1,
    )
    code_task_summary = code_task_summary["summary"]

    # Select branch name
    code_task_summary = edit_code_task_summary(code_task_summary)
    assert_exit(not code_task_summary, "Failed to edit code task summary.", exit_code=-1)
    code_task_summary = code_task_summary[0]

    # create and checkout branch
    print("Updating code task summary to config:")
    config_file = os.path.join(".chat", "complete.config")
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            config["taskDescription"] = code_task_summary
    else:
        config = {"taskDescription": code_task_summary}
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    print("Code task summary has updated")


if __name__ == "__main__":
    main()
