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
    if selected_data["text"] == "":
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
Add a documentation comment to the selected code. Please pay attention to using \
standard comment format, such as method comments, please explain parameters and return values. \
And just add the documents for the selected portion of the code.
Following the task requirements, modify only the selected portion of the code. \
Please ensure that the revised code segment maintains the same indentation as the \
selected code to seamlessly integrate with the existing code structure and maintain \
correct syntax. Keep all other information as it is. \
Here is the relevant context information for your reference:
1. Selected portion of the code: {selected_text}
"""


PROMPT_ZH = prompt = """
你的任务是：
使用中文给被选中的代码添加头部文档注释。请注意使用规范的注释格式，如方法注释请解释参数以及返回值。
根据任务要求，仅修改被选中部分的代码。请确保修改后的代码段与所选代码保持相同的缩进，\
以与现有代码结构无缝集成并保持正确的语法。保留所有其他信息不变。
以下是你可以参考的 context 信息：
1. 编辑器中被选中的代码：{selected_text}
"""


def get_prompt():
    ide_language = IDEService().ide_language()
    return PROMPT_ZH if ide_language == "zh" else PROMPT


@chat(prompt=get_prompt(), stream_out=True)
# pylint: disable=unused-argument
def add_docstring(selected_text, visible_text):
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
    response = add_docstring(selected_text=selected_text, visible_text=visible_text)

    # apply new code to editor
    new_code = extract_markdown_block(response)
    IDEService().diff_apply("", new_code)

    sys.exit(0)


if __name__ == "__main__":
    main()
