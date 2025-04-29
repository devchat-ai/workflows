### aider Guide

aider is an AI-assisted code editing tool that can modify code based on natural language instructions.

Purpose:
Automatically analyze and modify code files that have been added to aider based on user-provided instructions.

Usage Method:

1. Use the `/aider.files.add` command to add files that need to be processed
2. Enter the `/aider <message>` command, where `<message>` is the description of the task you want aider to perform
3. Wait for aider to generate suggested changes
4. View the Diff view of each file in the IDE and choose whether to accept the modifications
5. For changes across multiple files, the system will ask if you want to continue viewing changes in the next file after each file

Notes:

- Files must be added to aider before use, otherwise you will be prompted to use the 'aider.files.add' command
- You can use the `aider.files.remove` command to remove files from aider
- All changes will be displayed in the IDE as a Diff view, and you can decide whether to apply these changes
- aider uses OpenAI's API, please ensure that the API key is correctly set up

Example:
/aider Refactor this code to improve performance

Additional Information:
aider supports multiple programming languages and can perform code refactoring, bug fixing, performance optimization, and other tasks. It will analyze all files currently added and provide overall improvement suggestions.
