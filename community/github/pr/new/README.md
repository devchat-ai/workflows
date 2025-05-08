### new_pr

Create a new Pull Request.

#### Purpose

- Automatically generate PR title and description
- Simplify code review process

#### Usage Method

ExecuteCommand: `/github.new_pr [additional_info]`

- additional_info: Optional additional information

#### Operation Process

1. Get current branch information and related Issues
2. Generate PR title and description
3. Allow users to edit PR content
4. Create Pull Request

#### Notes

- Ensure that the current branch has uncommitted changes
- Requires permission to create PR
