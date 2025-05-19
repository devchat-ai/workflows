import os
import sys

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(ROOT_DIR)
from devchat.llm import chat_json  # noqa: E402
from git_api import (  # noqa: E402
    create_issue,
    get_issue_info_by_url,
    parse_sub_tasks,
    update_issue_body,
    update_task_issue_url,
)

from lib.workflow.common_util import assert_exit, editor, ui_edit  # noqa: E402

# Function to generate issue title and description using LLM
PROMPT = (
    "Following is parent issue content:\n"
    "{issue_content}\n\n"
    "Based on the following issue task: {task}"
    "suggest a title and a detailed description for a GitHub issue:\n\n"
    'Output format: {{"title": "<title>", "description": "<description>"}} '
)


@chat_json(prompt=PROMPT)
def generate_issue_content(issue_content, task):
    pass


@editor("Edit issue title:")
@editor("Edit issue description:")
def edit_issue(title, description):
    pass


@ui_edit(ui_type="radio", description="Select a task to create issue:")
def select_task(tasks):
    pass


def get_issue_json(issue_url):
    issue = get_issue_info_by_url(issue_url)
    assert_exit(not issue, f"Failed to retrieve issue with ID: {issue_url}", exit_code=-1)
    return {
        "id": issue["iid"],
        "web_url": issue["web_url"],
        "title": issue["title"],
        "description": issue["description"],
    }


# Main function
def main():
    print("start new_issue ...", end="\n\n", flush=True)

    assert_exit(len(sys.argv) < 2, "Missing argument.", exit_code=-1)
    issue_url = sys.argv[1]

    old_issue = get_issue_json(issue_url)
    assert_exit(not old_issue, "Failed to retrieve issue with: {issue_url}", exit_code=-1)
    tasks = parse_sub_tasks(old_issue["get_issue_json"])
    assert_exit(not tasks, "No tasks in issue description.")

    # select task from tasks
    [task] = select_task(tasks)
    assert_exit(task is None, "No task selected.")
    task = tasks[task]
    print("task:", task, end="\n\n", flush=True)

    print("Generating issue content ...", end="\n\n", flush=True)
    issue_json_ob = generate_issue_content(issue_content=old_issue, task=task)
    assert_exit(not issue_json_ob, "Failed to generate issue content.", exit_code=-1)

    issue_title, issue_body = edit_issue(issue_json_ob["title"], issue_json_ob["description"])
    assert_exit(not issue_title, "Issue creation cancelled.", exit_code=0)
    print("New Issue:", issue_title, "description:", issue_body, end="\n\n", flush=True)

    print("Creating issue ...", end="\n\n", flush=True)
    issue = create_issue(issue_title, issue_body)
    assert_exit(not issue, "Failed to create issue.", exit_code=-1)
    print("New Issue:", issue["web_url"], end="\n\n", flush=True)

    # update issue task with new issue url
    new_body = update_task_issue_url(old_issue["description"], task, issue["web_url"])
    assert_exit(not new_body, f"{task} parse error.")
    new_issue = update_issue_body(issue_url, new_body)
    assert_exit(not new_issue, "Failed to update issue description.")

    print("Issue tasks updated successfully!", end="\n\n", flush=True)


if __name__ == "__main__":
    main()
