# pr Command

The pr Command is a main command used for handling Pull Requests (PRs). It doesn't execute specific operations itself, but completes specific functions through sub-commands.

## Available Sub-commands

1. pr.review - Generate PR code review descriptions
2. pr.improve - Generate code suggestions for PR
3. pr.describe - Generate PR descriptions
4. pr.custom_suggestions - Generate custom code suggestions for PR

## Usage Method

To use the functions of the pr Command, call the corresponding sub-command using the following format:

/pr.<sub-command> <PR_URL>

For example:

- /pr.review https://github.com/devchat-ai/devchat/pull/301
- /pr.improve https://github.com/devchat-ai/devchat/pull/301
- /pr.describe https://github.com/devchat-ai/devchat/pull/301
- /pr.custom_suggestions https://github.com/devchat-ai/devchat/pull/301

## Sub-command Descriptions

1. pr.review: Analyzes PR and generates code review descriptions, helping reviewers quickly understand the content and impact of the PR.

2. pr.improve: Analyzes PR and provides code improvement suggestions, helping developers optimize their code.

3. pr.describe: Automatically generates a description for the PR, summarizing the main changes and purpose of the PR.

4. pr.custom_suggestions: Generates custom PR code suggestions based on specific requirements.

Please choose the appropriate sub-command according to your specific needs. Each sub-command focuses on different aspects of PR processing, helping you manage and improve Pull Requests more efficiently.
