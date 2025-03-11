import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common_util import assert_exit, editor  # noqa: E402
from devchat.llm import chat_json  # noqa: E402
from git_api import (  # noqa: E402
    get_issue_info_by_url,
    parse_sub_tasks,
    update_issue_body,
    update_sub_tasks,
)

TASKS_PROMPT = (
    "Following is my git issue content.\n"
    "{issue_data}\n\n"
    "Sub task in issue is like:- [ ] task name\n"
    "'[ ] task name' will be as sub task content\n\n"
    "Following is my idea to update sub tasks:\n"
    "{user_input}\n\n"
    "Please output all tasks in JSON format as:"
    '{{"tasks": ["[ ] task1", "[ ] task2"]}}'
)


@chat_json(prompt=TASKS_PROMPT)
def generate_issue_tasks(issue_data, user_input):
    pass


def to_task_str(tasks):
    task_str = ""
    for task in tasks:
        task_str += task + "\n"
    return task_str


@editor("Edit issue old tasks:")
@editor("Edit issue new tasks:")
def edit_issue_tasks(old_tasks, new_tasks):
    pass


@editor("Input ISSUE url:")
def input_issue_url(url):
    pass


@editor("How to update tasks:")
def update_tasks_input(user_input):
    pass


def get_issue_json(issue_url):
    issue = get_issue_info_by_url(issue_url)
    assert_exit(not issue, "Failed to retrieve issue with ID: {issue_id}", exit_code=-1)
    return {
        "id": issue["number"],
        "html_url": issue["html_url"],
        "title": issue["title"],
        "body": issue["body"],
    }


# Main function
def main():
    print("start issue tasks update ...", end="\n\n", flush=True)

    [issue_url] = input_issue_url("")
    assert_exit(not issue_url, "No issue url.")
    print("issue url:", issue_url, end="\n\n", flush=True)

    issue = get_issue_json(issue_url)
    old_tasks = parse_sub_tasks(issue["body"])

    print(f"```tasks\n{to_task_str(old_tasks)}\n```", end="\n\n", flush=True)

    [user_input] = update_tasks_input("")
    assert_exit(not user_input, "No user input")

    new_tasks = generate_issue_tasks(issue_data=issue, user_input=user_input)
    assert_exit(not new_tasks, "No new tasks.")
    print("new_tasks:", new_tasks, end="\n\n", flush=True)
    assert_exit(not new_tasks.get("tasks", []), "No new tasks.")
    print("new tasks:", to_task_str(new_tasks["tasks"]), end="\n\n", flush=True)
    new_tasks = new_tasks["tasks"]

    [old_tasks, new_tasks] = edit_issue_tasks(to_task_str(old_tasks), to_task_str(new_tasks))
    assert_exit(not new_tasks, "No new tasks.")
    print("new tasks:", new_tasks, end="\n\n", flush=True)

    new_body = update_sub_tasks(issue["body"], new_tasks.split("\n"))
    new_issue = update_issue_body(issue_url, new_body)
    assert_exit(not new_issue, "Failed to update issue body.")

    print("Issue tasks updated successfully!", end="\n\n", flush=True)


if __name__ == "__main__":
    main()
