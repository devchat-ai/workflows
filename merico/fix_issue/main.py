import os
import re
import json
import subprocess
import sys

from devchat.llm import chat, chat_completion_stream
from devchat.memory import FixSizeChatMemory

from lib.ide_service import IDEService


def extract_edits_block(text):
    """
    Extracts the first Markdown code block from the given text without the language specifier.

    :param text: A string containing Markdown text
    :return: The content of the first Markdown code block, or None if not found
    """
    index = text.find("```edits")
    if index == -1:
        return None
    else:
        start = index + len("```edits")
        end = text.find("```", start)
        if end == -1:
            return None
        else:
            return text[start:end]

def extract_markdown_block(text):
    """
    Extracts the first Markdown code block from the given text without the language specifier.

    :param text: A string containing Markdown text
    :return: The content of the first Markdown code block, or None if not found
    """
    edit_code = extract_edits_block(text)
    if edit_code:
        return edit_code

    pattern = r"```(?:\w+)?\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        block_content = match.group(1)
        return block_content
    else:
        # whether exist ```language?
        if text.find("```"):
            return None
        return text


# step 1 : get selected code
def get_selected_code():
    selected_data = IDEService().get_selected_range().dict()

    if selected_data["range"]["start"] == -1:
        return None, None, None

    if selected_data["range"]["start"]["line"] != selected_data["range"]["end"]["line"]:
        print("Please select the line code of issue reported.\n\n", file=sys.stderr)
        sys.exit(1)

    return selected_data["abspath"], selected_data["text"], selected_data["range"]["start"]["line"]


# step 2 : input issue descriptions
def input_issue_descriptions(file_path, issue_line_num):
    diagnostics = IDEService().get_diagnostics_in_range(file_path, issue_line_num, issue_line_num)
    if not diagnostics:
        return None

    # select first sonarlint diagnostic
    for diagnostic in diagnostics:
        if diagnostic.find("<sonar") > 0:
            return diagnostic
    return diagnostics[0]


# step 3 : call llm to generate fix solutions
SYSTEM_ROLE_DIFF= """
You are a code refactoring assistant. Your task is to refactor the user's code to fix lint diagnostics. You will be provided with a code snippet and a list of diagnostics. Your response should include two parts:

1. An explanation of the reason for the diagnostics and how to fix them.
2. The edited code snippet with the diagnostics fixed, using markdown format for clarity.

The markdown block for edits should look like this:

```edits
def hello():
    print("Call hello():")
+     print("hello")

...

- hello(20)
+ hello()
```
Or like this, if a variable is not defined:

```edits
...
+     cur_file = __file__
    print(cur_file)
```
Please note the following important points:

1. The new code should maintain the correct indentation. The "+ " sign is followed by two spaces for indentation, which should be included in the edited code.
2. In addition to outputting key editing information, sufficient context (i.e., key information before and after editing) should also be provided to help locate the specific position of the edited line.
3. Don't output all file lines, if some lines are unchanged, please use "..." to indicate the ignored lines.
4. Use "+ " and "- " at start of the line to indicate the addition and deletion of lines.

Here are some examples of incorrect responses:

Incorrect example 1, where the indentation is not correct:

```edits
def hello():
    print("Call hello():")
+   print("hello")
```
In this case, if the "+ " sign and the extra space are removed, the print("hello") statement will lack the necessary two spaces for correct indentation.

Incorrect example 2, where no other code lines are provided:

```edits
+ print("hello")
```
This is an incorrect example because without additional context, it's unclear where the new print("hello") statement should be inserted.
"""

SYSTEM_ROLE_CODEBLOCK = """
你是一个重构工程师，你需要根据错误描述，对代码进行问题修正，只需要关注描述的问题，不需要关注代码中的其他问题。

输出的修正代码中，如果修改了多个代码段，中间没有修改的代码段，请使用...表示。
每一个被修改的代码段，应该包含前后至少3行未修改的代码，作为修改代码段的边界表示。

输出一个代码块中，例如：
```edits
def hello():
    msg = "hello"
    print(msg)

...

if __name__ == "__main__":
    hello()
```
"""


LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-3.5-turbo-1106")
if LLM_MODEL in ["qwen2-72b-instruct", "qwen-long", "qwen-turbo", "Yi-34B-Chat", "deepseek-coder", "xinghuo-3.5"]:
    SYSTEM_ROLE = SYSTEM_ROLE_CODEBLOCK
else:
    SYSTEM_ROLE = SYSTEM_ROLE_DIFF
MESSAGES_A = [
    {
        "role": "system",
        "content": SYSTEM_ROLE,
    },
]

# step 3 : call llm to generate fix solutions
PROMPT = """

Here is the code file:

{file_content}

There is an issue in the following code:

{issue_line_code}

{issue_description}

Here is the rule description:

{rule_description}

Please focus only on the error described in the prompt. Other errors in the code should be disregarded.

"""

memory = FixSizeChatMemory(max_size=20, messages=MESSAGES_A)
@chat(prompt=PROMPT, stream_out=True, memory=memory)
def call_llm_to_generate_fix_solutions(
    file_content, issue_line_code, issue_description, rule_description
):
    pass


APPLY_SYSTEM_PROMPT = """
Your task is apply the fix solution to the code, output the whole new code in markdown code block format.

Here is the code file:
{file_content}

Here is the fix solution:
{fix_solution}

Some rules for output code:
1. Focus on the fix solution, don't focus on other errors in the code.
2. Don't change the indentation of the code.
3. Don't change lines which are not metioned in fix solution, for example, don't remove empty lines in code.

Please output only the whole new code which is the result of applying the fix solution, and output the whole code.
"""
@chat(prompt=APPLY_SYSTEM_PROMPT, stream_out=True, model="deepseek-coder")
def apply_fix_solution(file_content, fix_solution):
    pass


# current file content
def get_current_file_content(file_path, issue_line_num):
    try:
        return IDEService().get_collapsed_code(file_path, issue_line_num, issue_line_num)
    except Exception:
        print("Error reading file:", file=sys.stderr)
        return None


# get issue description
def get_rule_description(issue_description):
    def parse_source_code(text):
        pattern = r"<(\w+):(.+?)>"
        match = re.search(pattern, text)

        if match:
            source = match.group(1)
            code = match.group(2)
            return source, code
        else:
            return None, None

    issue_source, issue_code = parse_source_code(issue_description)
    if issue_source.find("sonar") == -1:
        return issue_description

    issue_id = issue_code.split(":")[-1]
    issue_language = issue_code.split(":")[0]

    tools_path = IDEService().get_extension_tools_path()
    rules_path = "sonar-rspec"

    rule_path = os.path.join(tools_path, rules_path, "rules", issue_id, issue_language, "rule.adoc")
    if os.path.exists(rule_path):
        with open(rule_path, "r", encoding="utf-8") as file:
            return file.read()
    return issue_description


def get_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception:
        print("Error reading file:", file=sys.stderr)
        return None

GLOBAL_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".chat", ".workflow_config.json")

def get_aider_python_path():
    """
    Retrieves the path to the Aider Python executable from the global configuration file.

    Returns:
        str or None: The path to the Aider Python executable if found in the configuration,
                     or None if the configuration file doesn't exist or the path is not set.
    """
    if os.path.exists(GLOBAL_CONFIG_PATH):
        with open(GLOBAL_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get('aider_python')
    return None

def run_aider(message, file_path):
    """
    Run the Aider tool to apply changes to a file based on a given message.

    This function executes the Aider tool with specific parameters to apply changes
    to the specified file. It captures and returns the output from Aider.

    Args:
        message (str): The message describing the changes to be made.
        file_path (str): The path to the file that needs to be modified.

    Returns:
        str: The output from the Aider tool, containing information about the changes made.

    Raises:
        SystemExit: If the Aider process returns a non-zero exit code, indicating an error.
    """
    python = get_aider_python_path()
    model = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo-1106')
    
    cmd = [
        python,
        "-m",
        "aider",
        "--model",
        f"openai/{model}",
        "--yes",
        "--no-auto-commits", 
        "--dry-run",
        "--no-pretty",
        "--message",
        message,
        file_path
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    has_started = False
    aider_output = ""
    for line in process.stdout:
        if "run with --help" in line or 'run "aider --help"' in line:
            has_started = True
            continue
        if has_started:
            aider_output += line
            print(line, end="", flush=True)

    return_code = process.wait()

    if return_code != 0:
        for line in process.stderr:
            print(f"Error: {line.strip()}", file=sys.stderr)
        sys.exit(return_code)

    return aider_output


def apply_changes(changes, file_path):
    """
    Apply the changes to the specified file using aider.

    Args:
        changes (str): The changes to be applied to the file.
        file_path (str): The path to the file where changes will be applied.

    This function creates a temporary file with the changes, then uses aider to apply
    these changes to the specified file. It handles the execution of aider and manages
    the output and potential errors.
    """
    changes_file = '.chat/changes.txt'
    os.makedirs(os.path.dirname(changes_file), exist_ok=True)
    with open(changes_file, 'w', encoding='utf-8') as f:
        f.write(changes)

    python = get_aider_python_path()
    model = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo-1106')

    cmd = [
        python,
        "-m",
        "aider",
        "--model",
        f"openai/{model}",
        "--yes",
        "--no-auto-commits",
        "--apply",
        changes_file,
        file_path
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    has_started = False
    for line in process.stdout:
        if "Model:" in line:
            has_started = True
            continue
        if has_started:
            print(line, end="", flush=True)

    return_code = process.wait()

    if return_code != 0:
        for line in process.stderr:
            print(f"Error: {line.strip()}", file=sys.stderr)
        sys.exit(return_code)

    os.remove(changes_file)


def main():
    """
    Main function to fix issues in the selected code.
    It retrieves the selected code, gets issue descriptions,
    generates fix solutions using LLM, and applies the changes.
    """
    print("start fix issue ...\n\n", flush=True)
    file_path, issue_line, issue_line_num = get_selected_code()
    if not file_path or not issue_line:
        print("No code selected. Please select the code line you want to fix.", file=sys.stderr)
        sys.exit(1)
    issue_description = input_issue_descriptions(file_path, issue_line_num)
    if not issue_description:
        print(
            "There are no issues to resolve on the current line. "
            "Please select the line where an issue needs to be resolved."
        )
        sys.exit(0)

    print("make llm prompt ...\n\n", flush=True)
    current_file_content = get_current_file_content(file_path, issue_line_num)
    rule_description = get_rule_description(issue_description)
    #print("Rule description:\n\n", rule_description, end="\n\n")

    print("call llm to fix issue ...\n\n", flush=True)

    # ===> 如果aider python已经安装，则直接调用aider来执行AI访问
    aider_python = get_aider_python_path()

    if aider_python and os.path.exists(aider_python):
        python_path = os.environ.get("PYTHONPATH", "")
        if python_path:
            # remove PYTHONPATH
            os.environ.pop("PYTHONPATH")
        # Use aider-based implementation
        message = f"""
Fix issue: {issue_description}
Which is reported at line: {issue_line}

Rule description: {rule_description}
"""
        changes = run_aider(message, file_path)
        if not changes:
            print("No changes suggested by aider.")
            sys.exit(0)

        print("\nApplying changes...\n", flush=True)

        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        apply_changes(changes, file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        os.environ["PYTHONPATH"] = python_path

        # Display changes in IDE
        IDEService().select_range(file_path, -1, -1, -1, -1)
        IDEService().diff_apply("", updated_content, False)
    else:
        print("No aider python found, using default implementation.", end="\n\n")
        fix_solutions = call_llm_to_generate_fix_solutions(
            file_content=current_file_content,
            issue_line_code=issue_line,
            issue_description=issue_description,
            rule_description=rule_description,
        )
        if not fix_solutions:
            sys.exit(1)

        print("\n\n", flush=True)

        print("apply fix solution ...\n\n")
        # updated_content = apply_fix_solution(file_content=get_file_content(file_path), fix_solution=fix_solutions)
        # if not updated_content:
        #     print("No edits code generated.")
        #     sys.exit(0)
        # updated_content = fix_solutions['content']
        updated_content = extract_markdown_block(fix_solutions)
        if updated_content:
            # Display changes in IDE
            IDEService().diff_apply("", updated_content, True)

    print("Changes have been displayed in the IDE.")


if __name__ == "__main__":
    main()
