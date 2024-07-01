import os
import re
import sys

from devchat.llm import chat

from lib.ide_service import IDEService


def extract_markdown_block(text):
    """
    Extracts the first Markdown code block from the given text without the language specifier.

    :param text: A string containing Markdown text
    :return: The content of the first Markdown code block, or None if not found
    """
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

    return selected_data['abspath'], selected_data['text'], selected_data["range"]["start"]["line"]


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
PROMPT = """
You are a code refactoring assistant.
This is my code file:
{file_content}

There is a issue in the following code:
{issue_line_code}
{issue_description}

Here is the rule description:
{rule_description}

Please provide me refactor code to fix this issue.
"""
@chat(prompt=PROMPT, stream_out=True)
def call_llm_to_generate_fix_solutions(file_content, issue_line_code, issue_description, rule_description):
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
        pattern = r'<(\w+):(.+?)>'
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

    issue_id = issue_code.split(':')[-1]
    issue_language = issue_code.split(':')[0]

    tools_path = IDEService().get_extension_tools_path()
    rules_path = "sonar-rspec"

    rule_path = os.path.join(tools_path, rules_path, "rules", issue_id, issue_language, "rule.adoc")
    if os.path.exists(rule_path):
        with open(rule_path, "r", encoding="utf-8") as file:
            return file.read()
    return issue_description


# step 4 : apply fix solutions to code
def apply_fix_solutions_to_code():
    pass


# step 0: try parse user input
def try_parse_user_input():
    pass


def main():
    print("start fix issue ...\n\n")
    file_path, issue_line, issue_line_num = get_selected_code()
    if not file_path or not issue_line:
        print('No code selected. Please select the code line you want to fix.', file=sys.stderr)
        sys.exit(1)
    issue_description = input_issue_descriptions(file_path, issue_line_num)
    if not issue_description:
        print('There are no issues to resolve on the current line. '
              'Please select the line where an issue needs to be resolved.')
        sys.exit(0)

    print("make llm prompt ...\n\n")
    current_file_content = get_current_file_content(file_path, issue_line_num)
    rule_description = get_rule_description(issue_description)
    print("--->>:", rule_description)

    print("call llm to fix issue ...\n\n")
    fix_solutions = call_llm_to_generate_fix_solutions(
        file_content=current_file_content,
        issue_line_code=issue_line,
        issue_description=issue_description,
        rule_description=rule_description)
    if not fix_solutions:
        sys.exit(1)


if __name__ == "__main__":
    main()
