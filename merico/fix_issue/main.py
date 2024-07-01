import os
import re
import sys

from devchat.llm import chat
from devchat.memory import FixSizeChatMemory

from lib.ide_service import IDEService

PROMPT = prompt = """
file: {file_path}
```
{selected_text}
```
"""

PROMPT_ZH = prompt = """
文件: {file_path}
```
{selected_text}
```

输出内容使用中文，我的母语为中文。
"""


def get_prompt():
    ide_language = IDEService().ide_language()
    return PROMPT_ZH if ide_language == "zh" else PROMPT


MESSAGES_A = [
    {
        "role": "system",
        "content": """
Your task is:
Write a documentation comment to the selected code. Please pay attention to using \
standard comment format, such as method comments, please explain parameters and return values. \
And just add the documents for the selected portion of the code.
Output documentation comment is format as code block.\

You must follow the following rules:
1. Output documentation comment in ```comment <documentation comments without code lines> ``` \
    format.
2. Different languages have different comment symbols, please choose the correct comment symbol \
    according to the file name.
3. You must output ... to indicate the remaining code, output all code block can make more errors.
""",
    },
    {
        "role": "user",
        "content": """
file: a1.py
```
    def print_hello():
        print("hello")
        print("world")
```
""",
    },
    {
        "role": "assistant",
        "content": """
```comment
    def print_hello():
        \"\"\"
        print hello

        Parameters:
        None

        Returns:
        None
        \"\"\"
        print("hello")
        ...
```
""",
    },
    {
        "role": "user",
        "content": """
file: t1.java
```
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
```
""",
    },
    {
        "role": "assistant",
        "content": """
```comment
    /**
     * The main method is the entry point of the program.
     * This method prints "Hello, World!" to the console.
     *
     * @param args command line arguments (not used in this program)
     */
    public static void main(String[] args) {
        ...
```
""",
    },
    {
        "role": "user",
        "content": """
file: t1.py
```
def content_to_json(content):
    try:
        content_no_block = _try_remove_markdown_block_flag(content)
        response_obj = json.loads(content_no_block)
        return response_obj
    except json.JSONDecodeError as err:
        raise RetryException(err) from err
    except Exception as err:
        raise err
```
""",
    },
    {
        "role": "assistant",
        "content": """
```comment
def content_to_json(content):
    \"\"\"
    Convert the given content to a JSON object.

    Parameters:
    content (str): The content to convert.

    Returns:
    dict: The JSON object.

    Raises:
    RetryException: If the content cannot be decoded to JSON.
    \"\"\"
    try:
        ...
```
""",
    },
]




memory = FixSizeChatMemory(max_size=20, messages=MESSAGES_A)


@chat(prompt=get_prompt(), stream_out=True, memory=memory)
# pylint: disable=unused-argument
def add_docstring(selected_text, file_path):
    """
    call ai to rewrite selected code
    """
    pass  # pylint: disable=unnecessary-pass


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


def get_indent_level(text):
    """
    Returns the indentation level of the given text.

    :param text: A string containing the text to be analyzed
    :return: The indentation level of the text, as an integer
    """
    indent_level = 0
    for char in text:
        if char == " ":
            indent_level += 1
        elif char == "\t":
            indent_level += 4
        else:
            break
    return indent_level


def offset_indent_level(text, indent_level):
    """
    Offsets the indentation level of the given text by the specified amount.

    :param text: A string containing the text to be modified
    :param indent_level: The amount by which to offset the indentation level
    :return: The modified text with the indentation level offset
    """
    current_indent = get_indent_level(text)
    offset_indent = indent_level - current_indent
    if offset_indent > 0:
        lines = text.splitlines()
        new_lines = []
        for line in lines:
            new_lines.append(" " * offset_indent + line)
        text = "\n".join(new_lines)
    return text


def merge_code(selected_text, docstring):
    user_selected_lines = selected_text.split("\n")
    docstring_lines = docstring.split("\n")

    user_selected_trim_lines = [line.replace(" ", "").strip() for line in user_selected_lines]
    docstring_trim_lines = [line.replace(" ", "").strip() for line in docstring_lines]

    # match user_selected_trim_line == docstring_trim_line
    #    and index_selected_line != index_docstring_line
    has_match = False
    for index, line in enumerate(user_selected_trim_lines):
        for index_doc, line_doc in enumerate(docstring_trim_lines):
            if line_doc == "..." and has_match:
                line_doc = line
                break
            if line == line_doc:
                has_match = True
                break
        if line != line_doc or index == index_doc:
            continue
        return "\n".join(docstring_lines[:index_doc] + user_selected_lines[index:])

    # match with part of code
    for index, line in enumerate(user_selected_trim_lines):
        for index_doc, line_doc in enumerate(docstring_trim_lines):
            if line_doc == "...":
                break
            if (
                line.strip().find(line_doc.strip()) != -1
                or line_doc.strip().find(line.strip()) != -1
            ):
                break
        if (
            line.strip().find(line_doc.strip()) == -1 and line_doc.strip().find(line.strip()) == -1
        ) or index == index_doc:
            continue
        return "\n".join(docstring_lines[:index_doc] + user_selected_lines[index:])
    return docstring + "\n" + selected_text


def main():
    # Prepare code
    selected_text = get_selected_code()

    # Rewrite
    response = add_docstring(
        selected_text=selected_text.get("text", ""), file_path=selected_text.get("abspath", "")
    )
    if not response:
        sys.exit(1)

    # Get indent level
    indent = get_indent_level(selected_text.get("text", ""))

    # Apply new code to editor
    new_code = extract_markdown_block(response)
    if not new_code:
        language = IDEService().ide_language()
        print_message(language)
        sys.exit(0)

    # Offset indent level
    new_code = offset_indent_level(new_code, indent)

    # Merge code
    docstring_code = merge_code(selected_text.get("text", ""), new_code)
    # Apply diff
    IDEService().diff_apply("", docstring_code)

    sys.exit(0)


def print_message(language):
    if language == "zh":
        print("\n\n大模型输出不完整，不能进行代码操作。\n\n")
    else:
        print("\n\nThe output of the LLM is incomplete and cannot perform code operations.\n\n")


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
    # Remove 1 unexpected arguments; 'hello' expects 0 positional arguments. [+2 locations] <sonarlint:python:S930>
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
        print('There are no issues to resolve on the current line. Please select the line where an issue needs to be resolved.')
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
