import os
import sys

from devchat.llm import chat_json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common_util import assert_exit, editor  # noqa: E402
from git_api import create_issue  # noqa: E402

# Function to generate issue title and body using LLM
PROMPT = (
    "Based on the following description, "
    "suggest a title and a detailed body for a GitHub issue:\n\n"
    "Description: {description}\n\n"
    'Output format: {{"title": "<title>", "body": "<body>"}} '
)


@chat_json(prompt=PROMPT)
def generate_issue_content(description):
    pass


@editor("Edit issue title:")
@editor("Edit issue body:")
def edit_issue(title, body):
    pass


# Main function
def main():
    print("start new_issue ...", end="\n\n", flush=True)

    assert_exit(len(sys.argv) < 2, "Missing argument.", exit_code=-1)
    description = sys.argv[1]

    print("Generating issue content ...", end="\n\n", flush=True)
    issue_json_ob = generate_issue_content(description=description)
    assert_exit(not issue_json_ob, "Failed to generate issue content.", exit_code=-1)

    issue_title, issue_body = edit_issue(issue_json_ob["title"], issue_json_ob["body"])
    assert_exit(not issue_title, "Issue creation cancelled.", exit_code=0)
    print("New Issue:", issue_title, "body:", issue_body, end="\n\n", flush=True)

    print("Creating issue ...", end="\n\n", flush=True)
    issue = create_issue(issue_title, issue_body)
    assert_exit(not issue, "Failed to create issue.", exit_code=-1)
    print("New Issue:", issue["html_url"], end="\n\n", flush=True)


if __name__ == "__main__":
    main()
