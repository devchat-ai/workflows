### code_task_summary

Generate a code task summary based on the current branch or specified Issue.

#### Purpose

- Automatically generate concise code task descriptions
- Help developers quickly understand task key points
- Use for updating project configuration or documentation

#### Usage Method

ExecuteCommand: `/github.code_task_summary [issue_url]`

- If issue_url is not provided, Issue information will be extracted based on the current branch name
- If issue_url is provided, the content of that Issue will be used directly

#### Operation Process

1. Get Issue information
2. Generate code task summary
3. Allow user to edit summary
4. Update project configuration file

#### Notes

- Ensure that Git repository is configured correctly
- Valid GitLab Token is needed to access API
