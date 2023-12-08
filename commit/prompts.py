# ruff: noqa

# summary changes for files based diff
# diff => {__DIFF__}
PROMPT_SUMMARY_FOR_FILES = """ 
Objective: **Create concise summaries for each modified file based on the provided diff changes and any additional user input.**

**Instructions:**
1. Review the diff changes and user input to understand the context and content of the modifications.
2. Write a summary for each file that has been modified, capturing the essence of the changes.
3. Use the filename from the diff as the key, and the summary as the value in the output JSON object.

**Response Format:**
```json
{
  \"filename1 with path\": \"Summary of the changes made in filename1\",
  \"filename2 with path\": \"Summary of the changes made in filename2\",
  ...
}
```

**Constraints:**
- Ensure that the summaries are accurate and reflect the changes made.
- Ensure that the summary is concise and does not exceed 200 characters.
- The response must be in JSON format, with filenames as keys and summaries as values.
- Do not include any additional text or output outside of the JSON format.
- The keys in the JSON object should correspond to real filenames present in the diff changes.

**User Input:**
```
{__USER_INPUT__}
```

**Diff Changes:**
```
{__DIFF__}
```
---

Based on the provided diff changes and any additional user input, please generate a JSON object containing summaries for each modified file.
"""
prompt_summary_for_files_llm_config = {"model": "gpt-3.5-turbo-1106"}
# ask summaries for missed files
# missed files => {__MISSED_FILES__}
PROMPT_SUMMARY_FOR_FILES_RETRY = """
The following files are missed in your summary:
{__MISSED_FILES__}
"""

# group changes for files based diff
# diff => {__DIFF__}
PROMPT_GROUP_FILES = """
Objective: **Categorize the modified files from a diff into groups based on their relevance to each other, and assign an importance level to each group. Limit the number of groups to a maximum of three.**

**Instructions:**
1. **Analysis:** Review the diff content to discern related changes. Group files that are part of the same logical change, ensuring that the code will compile and run correctly post-commit.
2. **Atomic Grouping:** Aim for the smallest possible groups. Each should represent a single, cohesive modification for clarity and independent comprehension. Do not exceed three groups in total.
3. **Importance Level:** Rate each group's importance on a scale of 1 to 10, with 1 being the most critical. Consider the impact on functionality, urgency of fixes, and feature significance.

**Response Format:**
- Use JSON format for your response.
- Include all files from the diff content.
- Structure the JSON as shown in the example below.

**Example Output:**
```json
{
    "groups": [
		{\"files\": [\"fileA\", \"fileB\"], \"group\": \"Feature Improvement\", \"importance_level\": 5},
		{\"files\": [\"fileC\"], \"group\": \"Bug Fix\", \"importance_level\": 1},
		{\"files\": [\"fileD\", \"fileE\"], \"group\": \"Code Refactoring\", \"importance_level\": 3}
	]
}
```

**Constraints:**
- Ensure the JSON output is valid and contains no additional text or characters.
- Each group must be self-contained, with no cross-group dependencies.
- The importance level should accurately reflect the priority for committing the changes.
- The total number of groups must not exceed three.
- Follows the JSON structure shown in the example above.

**Diff Content:**
```
{__DIFF__}
```

---

Based on the provided diff content, group the files accordingly and assign an appropriate importance level to each group, following the instructions and constraints.
"""
prompt_group_files_llm_config = {"model": "gpt-3.5-turbo-1106"}
# re-group files based missed files
# missed files => {__MISSED_FILES__}
PROMPT_GROUP_FILES_RETRY = """
The following files are missed in your response:
{__MISSED_FILES__}
Please re-group the files again, don't miss any file.
"""


# generate commit message based diff and user_input
# diff => {__DIFF__}
# user_input => {__USER_INPUT__}
PROMPT_COMMIT_MESSAGE_BY_DIFF_USER_INPUT = """
Objective:** Create a commit message that concisely summarizes the changes made to the codebase as reflected by the provided diff. The commit message should also take into account any additional context or instructions given by the user.

**Commit Message Structure:**
1. **Title Line:** Start with a type from the following options: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, etc. Follow the type with a concise title. Format: `type: Title`. Only one title line is allowed.
2. **Summary:** Provide a summary of all changes in no more than three detailed message lines. Each line should be prefixed with a \"-\".
3. **Closing Reference (Optional):** If applicable, include a closing reference line in the format `Closes #IssueNumber`. Only include this if you know the exact issue number.

**Response Format:**
```
type: Title

 Detail message line 1
 Detail message line 2
 Detail message line 3

Closes #IssueNumber
```

**Constraints:**
- Do not include markdown block flags (```) or the placeholder text \"commit_message\" in your response.
- Adhere to best practices for commit messages:
  - Keep the title under 50 characters.
  - Keep each summary line under 72 characters.
- If the exact issue number is unknown, omit the closing reference line.

**User Input:** `{__USER_INPUT__}`

**Code Changes:**
```
{__DIFF__}
```
---

Please use the above structure to generate a commit message that meets the specified criteria.
"""
prompt_commit_message_by_diff_user_input_llm_config = {"model": "gpt-3.5-turbo-1106"}

# generate commit message based file summary and user_input
# file_summary => {__FILE_SUMMARY__}
# user_input => {__USER_INPUT__}
PROMPT_COMMIT_MESSAGE_BY_SUMMARY_USER_INPUT = """
Objective:** Generate a commit message that accurately reflects the changes made to the codebase, as summarized by the AI-generated file summary and any additional user input.

**Commit Message Structure:**
1. **Title Line:** Begin with a type from the following options: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, etc. The title should be concise and informative. Format: `type: Title`. Only one title line is allowed.
2. **Summary:** Condense the changes into 1-3 detailed message lines, each beginning with a \"-\".
3. **Closing Reference (Optional):** If known, include a closing reference in the format `Closes #IssueNumber`. If the exact issue number is unknown, omit this line.

**Response Format:**
```
type: Title

 Detail message line 1
 Detail message line 2
 Detail message line 3

Closes #IssueNumber
```

**Constraints:**
- Exclude markdown code block flags (```) and the placeholder \"commit_message\" from your response.
- Follow commit message best practices:
  - Title line should be under 50 characters.
  - Each summary line should be under 72 characters.
- If the issue number is not provided, do not include the closing reference line.

**User Input:** `{__USER_INPUT__}`

**File Summary:**
```
{__FILE_SUMMARY__}
```

---

Please create a commit message following the above guidelines based on the provided file summary and user input.
"""
prompt_commit_message_by_summary_user_input_llm_config = {"model": "gpt-4-1106-preview"}
