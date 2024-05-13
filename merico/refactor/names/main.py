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
file: {file_path}
```
{selected_text}
```
"""


def get_prompt():
    ide_language = IDEService().ide_language()
    return PROMPT_ZH if ide_language == "zh" else PROMPT


MESSAGES_A = [
    {
        "role": "system",
        "content": """
Your task is:
Refine internal variable and function names within the code to achieve concise and \
    meaningful identifiers that comply with English naming conventions.

Rules:
1. Don't rename a call or global variable. for example, xx() is function call, xx \
    is a bad name, but you MUST not rename it .
2. You can rename a local variable or parameter variable name.
3. Current function's name can be renamed. Always this is a new function.

""",
    },
    {
        "role": "user",
        "content": """
file: a1.py
```
    def print_hello():
        a = "hello world"
        print(a)
```
""",
    },
    {
        "role": "assistant",
        "content": """
```python
    def print_hello():
        msg = "hello world"
        print(msg)
```
""",
    },
    {
        "role": "user",
        "content": """
file: t1.py
```
    def print_hello(a: str):
        print(a)
```
""",
    },
    {
        "role": "assistant",
        "content": """
```python
    def print_hello(msg: str):
        print(msg)
```
""",
    },
    {
        "role": "user",
        "content": """
file: t1.py
```
    def some():
        print("hello")
```
""",
    },
    {
        "role": "assistant",
        "content": """
```python
    def output_hello():
        print("hello")
```
""",
    },
    {
        "role": "user",
        "content": """
file: t1.py
```
    def print_hello():
        print("hello")
```
""",
    },
    {
        "role": "assistant",
        "content": """
```python
    def print_hello():
        output("hello")
```
""",
    },
    {
        "role": "user",
        "content": """
Your response is error, you changed call name.
print is a function call, if you rename it, this will make a compile error.
""",
    },
    {
        "role": "assistant",
        "content": """
```python
    def print_hello():
        print("hello")
```
""",
    },
]


def get_selected_code():
    """
    Retrieves the selected lines of code from the user's selection.

    This function extracts the text selected by the user in their IDE or text editor.
    If no text has been selected, it prints an error message to stderr and exits the
    program with a non-zero status indicating failure.

    Returns:
        dict: A dictionary containing the key 'selectedText' with the selected text
        as its value. If no text is selected, the program exits.
    """
    selected_data = IDEService().get_selected_range().dict()

    miss_selected_error = "Please select some text."
    if selected_data["range"]["start"] == selected_data["range"]["end"]:
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_text = f.read()
                print(readme_text)
                sys.exit(0)

        print(miss_selected_error, file=sys.stderr, flush=True)
        sys.exit(-1)

    return selected_data


memory = FixSizeChatMemory(max_size=20, messages=MESSAGES_A)


@chat(prompt=get_prompt(), stream_out=True, memory=memory)
# pylint: disable=unused-argument
def reanme_variable(selected_text, file_path):
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


def remove_unnecessary_escapes(code_a, code_b):
    code_copy = code_b  # Create a copy of the original code
    escape_chars = re.finditer(r"\\(.)", code_b)

    remove_char_index = []
    for match in escape_chars:
        before = code_b[max(0, match.start() - 4) : match.start()]
        after = code_b[match.start() + 1 : match.start() + 5]
        substr = before + after
        if substr in code_a:
            remove_char_index.append(match.start())

    # visit remove_char_index in reverse order
    remove_char_index.reverse()
    for index in remove_char_index:
        code_copy = code_copy[:index] + code_copy[index + 1 :]
    return code_copy


def main():
    # prepare code
    selected_text = get_selected_code()
    selected_code = selected_text.get("text", "")
    selected_file = selected_text.get("abspath", "")

    # rewrite
    response = reanme_variable(selected_text=selected_code, file_path=selected_file)

    # apply new code to editor
    new_code = extract_markdown_block(response)
    if not new_code:
        if IDEService().ide_language() == "zh":
            print("\n\n大模型输出不完整，不能进行代码操作。\n\n")
        else:
            print("\n\nThe output of the LLM is incomplete and cannot perform code operations.\n\n")
        sys.exit(0)

    new_code = remove_unnecessary_escapes(selected_text.get("text", ""), new_code)
    IDEService().diff_apply("", new_code)

    sys.exit(0)


if __name__ == "__main__":
    main()
