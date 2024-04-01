import re
import os
import sys

from devchat.ide.service import IDEService
from devchat.ide.vscode_services import selected_lines, visible_lines
from devchat.llm import chat


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
    if selected_data["text"] == "":
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_text = f.read()
                print(readme_text)
                sys.exit(0)

        print(miss_selected_error, file=sys.stderr, flush=True)
        sys.exit(-1)

    return selected_data


def get_visible_code():
    """
    Retrieves visible code from the visible_lines function.

    Returns:
    visible_data: The visible code retrieved from the visible_lines function.
    """
    visible_data = IDEService().get_visible_range().dict()
    return visible_data


PROMPT = prompt = """
Your task is:

Try to find potential bugs in the selected code and fix it. \
Please only fix and modify the selected portion of the code and giving out the fixed code. \
Do not show the original code in your results. \
Explain the bugs and fixes at last.

Following the task requirements, please ensure that the revised code segment \
maintains the same indentation as the selected code to seamlessly integrate with \
the existing code structure and maintain correct syntax.
Giving the results in the following format:

Fixed code:
```language
The fixed code goes here...
```

Bugs and fixes:
1. Bug1 and its fixes...;
2. Bug2 and its fixes...;
...

Here is the relevant context information for your reference:
1. Selected portion of the code: {selected_text}
2. Visible portion of the code: {visible_text}
"""


PROMPT_ZH = prompt = """
你的任务是：

尝试找到所选代码中的潜在错误并修复它。 \
请仅修复和修改代码中选定的部分并给出修复后的代码。 \
不要在结果中显示原始代码。 \
最后解释一下错误和修复。

按照任务要求，请确保修改后的代码段保持与所选代码相同的缩进，以与现有的代码结构无缝集成并保持正确的语法。
以以下格式给出结果：

已修复代码：
```language
已修复代码放在这里...
```

问题及修复：

1. Bug1 及其修复...；
2. Bug2 及其修复...；
...

以下是相关上下文信息，供您参考：
1. 选定的代码部分：{selected_text}
2.代码可见部分：{visible_text}
"""


def get_prompt():
    ide_language = IDEService().ide_language()
    return PROMPT_ZH if ide_language == "zh" else PROMPT


@chat(prompt=get_prompt(), stream_out=True)
# pylint: disable=unused-argument
def fix_bugs(selected_text, visible_text):
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
        return None


def main():
    # prepare code
    selected_text = get_selected_code()
    visible_text = get_visible_code()

    # rewrite
    response = fix_bugs(selected_text=selected_text, visible_text=visible_text)

    # apply new code to editor
    new_code = extract_markdown_block(response)
    if new_code is not None:
        IDEService().diff_apply("", new_code)

    sys.exit(0)


if __name__ == "__main__":
    main()
