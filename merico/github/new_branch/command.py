import json
import os
import sys

from devchat.llm import chat_json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common_util import assert_exit, ui_edit  # noqa: E402
from git_api import (  # noqa: E402
    check_git_installed,
    create_and_checkout_branch,
    is_issue_url,
    read_issue_by_url,
    save_last_base_branch,
)

# Function to generate a random branch name
PROMPT = (
    "Give me 5 different git branch names, "
    "mainly hoping to express: {task}, "
    "Good branch name should looks like: <type>/<main content>,"
    "the final result is output in JSON format, "
    'as follows: {{"names":["name1", "name2", .. "name5"]}}\n'
)


@chat_json(prompt=PROMPT)
def generate_branch_name(task):
    pass


@ui_edit(ui_type="radio", description="Select a branch name")
def select_branch_name_ui(branch_names):
    pass


def select_branch_name(branch_names):
    [branch_selection] = select_branch_name_ui(branch_names)
    assert_exit(branch_selection is None, "No branch selected.", exit_code=0)
    return branch_names[branch_selection]


def get_issue_or_task(task):
    if is_issue_url(task):
        issue = read_issue_by_url(task.strip())
        assert_exit(not issue, "Failed to read issue.", exit_code=-1)

        return json.dumps(
            {"id": issue["number"], "title": issue["title"], "body": issue["body"]}
        ), issue["number"]
    else:
        return task, None


# Main function
def main():
    print("Start create branch ...", end="\n\n", flush=True)

    is_git_installed = check_git_installed()
    assert_exit(not is_git_installed, "Git is not installed.", exit_code=-1)

    task = sys.argv[1]
    assert_exit(
        not task,
        "You need input something about the new branch, or input a issue url.",
        exit_code=-1,
    )

    # read issue by url
    task, issue_id = get_issue_or_task(task)

    # Generate 5 branch names
    print("Generating branch names ...", end="\n\n", flush=True)
    branch_names = generate_branch_name(task=task)
    assert_exit(not branch_names, "Failed to generate branch names.", exit_code=-1)
    branch_names = branch_names["names"]
    for index, branch_name in enumerate(branch_names):
        if issue_id:
            branch_names[index] = f"{branch_name}-#{issue_id}"

    # Select branch name
    selected_branch = select_branch_name(branch_names)

    # save base branch name
    save_last_base_branch()

    # create and checkout branch
    print(f"Creating and checking out branch: {selected_branch}")
    create_and_checkout_branch(selected_branch)
    print("Branch has create and checkout")


if __name__ == "__main__":
    main()
