import os
import re
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
Add necessary line comments to the selected lines of code. Please keep in mind to ensure:
1. Just add comments only for the selected portion of the code, \
do not modify any thing beyond the selected portion;
2. Add these comments above the corresponding lines of code;
3. Output only the selected portion of the code with comments added;
4. Maintains the same indentation as the selected portion of the code;
5. Do not show any code beyond the selected portion;
Following the task requirements, please ensure that the revised code segment \
maintains the same indentation as the selected code to seamlessly integrate with \
the existing code structure and maintain correct syntax.
Here is the relevant context information for your reference:
1. Selected portion of the code: {selected_text}
2. Visible portion of the code: {visible_text}
"""


PROMPT_ZH = prompt = """
你的任务是：
使用中文给被选中的代码添加必要的注释。
根据任务要求，仅修改被选中部分的代码。请确保修改后的代码段与所选代码保持相同的缩进，\
以与现有代码结构无缝集成并保持正确的语法。保留所有其他信息不变。
以下是你可以参考的 context 信息：
1. 编辑器中被选中的代码：{selected_text}
2. 当前编辑器中可见代码：{visible_text}
"""


def get_prompt():
    ide_language = IDEService().ide_language()
    return PROMPT_ZH if ide_language == "zh" else PROMPT


@chat(prompt=get_prompt(), stream_out=True)
# pylint: disable=unused-argument
def add_comments(selected_text, visible_text):
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
        return text


def main():
    # prepare code
    selected_text = get_selected_code()
    visible_text = get_visible_code()

    # rewrite
    response = add_comments(selected_text=selected_text, visible_text=visible_text)

    # apply new code to editor
    new_code = extract_markdown_block(response)
    IDEService().diff_apply("", new_code)

    sys.exit(0)


if __name__ == "__main__":
    main()
