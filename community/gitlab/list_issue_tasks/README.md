### list_issue_tasks

List the tasks in a specified Issue.

#### Purpose

- View subtasks within an Issue
- Track task progress

#### Usage Method

ExecuteCommand: `/github.list_issue_tasks <issue_url>`

#### Operation Process

1. Get information for the specified Issue
2. Parse task lists in the Issue content
3. Display the task list

#### Notes

- A valid Issue URL must be provided
- Tasks should be listed in a specific format in the Issue (e.g., - [ ] task description)
