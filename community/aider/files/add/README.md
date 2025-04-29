### aider.files.add

This Command is used to add files to aider's processing list.

Purpose:
Add specified files to aider, including them in subsequent aider operations.

Usage Method:
/aider.files.add <file_path>

Parameters:

- <file_path>: The file path to add (required)

Notes:

- The file path must be in a valid format
- Files already in the list will not be added again
- After successful addition, the current aider file list will be displayed

Example:
/aider.files.add src/main.py

Additional Information:
This Command saves the file path to the .chat/.aider_files file. If the .chat directory does not exist, it will be created automatically.
