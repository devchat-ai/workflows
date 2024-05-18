import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from devchat.llm import chat_json  # noqa: E402
from git_api import create_issue, parse_sub_tasks, update_task_issue_url, update_issue_body, get_issue_info_by_url  # noqa: E402
from common_util import editor, assert_exit, ui_edit  # noqa: E402


# Function to generate issue title and body using LLM
PROMPT = (
    "Following is parent issue content:\n"
    "{issue_content}\n\n"
    "Based on the following issue task: {task}"
    "suggest a title and a detailed body for a GitHub issue:\n\n"
    "Output format: {{\"title\": \"<title>\", \"body\": \"<body>\"}} ")
@chat_json(prompt=PROMPT)
def generate_issue_content(issue_content, task):
    pass


@editor("Edit issue title:")
@editor("Edit issue body:")
def edit_issue(title, body):
    pass


@ui_edit(ui_type="radio", description="Select a task to create issue:")
def select_task(tasks):
    pass

def get_issue_json(issue_url):
    issue = get_issue_info_by_url(issue_url)
    assert_exit(not issue, "Failed to retrieve issue with ID: {issue_id}", exit_code=-1)
    return {"id": issue["number"], "html_url": issue["html_url"], "title": issue["title"], "body": issue["body"]}


# Main function
def main():
    print("start new_issue ...", end="\n\n", flush=True)
    
    assert_exit(len(sys.argv) < 2, "Missing argument.", exit_code=-1)
    issue_url = sys.argv[1]

    old_issue = get_issue_json(issue_url)
    assert_exit(not old_issue, "Failed to retrieve issue with: {issue_url}", exit_code=-1)
    tasks = parse_sub_tasks(old_issue["body"])
    assert_exit(not tasks, "No tasks in issue body.")


    # select task from tasks
    [task] = select_task(tasks)
    assert_exit(task is None, "No task selected.")
    task = tasks[task]
    print("task:", task, end="\n\n", flush=True)
    
    print("Generating issue content ...", end="\n\n", flush=True)
    issue_json_ob = generate_issue_content(issue_content=old_issue, task=task)
    assert_exit(not issue_json_ob, "Failed to generate issue content.", exit_code=-1)
    
    issue_title, issue_body = edit_issue(issue_json_ob["title"], issue_json_ob["body"])
    assert_exit(not issue_title, "Issue creation cancelled.", exit_code=0)
    print("New Issue:", issue_title, "body:", issue_body, end="\n\n", flush=True)

    print("Creating issue ...", end="\n\n", flush=True)
    issue = create_issue(issue_title, issue_body)
    assert_exit(not issue, "Failed to create issue.", exit_code=-1)
    print("New Issue:", issue["html_url"], end="\n\n", flush=True)

    # update issue task with new issue url
    new_body = update_task_issue_url(old_issue["body"], task, issue["html_url"])
    assert_exit(not new_body, f"{task} parse error.")
    new_issue = update_issue_body(issue_url, new_body)
    assert_exit(not new_issue, "Failed to update issue body.")

    print("Issue tasks updated successfully!", end="\n\n", flush=True)


if __name__ == "__main__":
    main()