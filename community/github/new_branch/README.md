### new_branch

Create a new branch based on the current branch and switch to it.

#### Purpose

- Quickly create new feature or bugfix branches
- Keep work areas isolated

#### Usage Method

ExecuteCommand: `/github.new_branch <description>`

- description: Brief description of the new branch or related Issue URL

#### Operation Process

1. Generate multiple branch name suggestions
2. User selects or edits branch name
3. Create new branch and switch to it

#### Notes

- Ensure that changes in the current branch have been committed
- If an Issue URL is provided, the Issue number will be automatically associated with the branch name
