import sys
import os

from devchat.ide.service import IDEService
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


EXPLAIN_PROMPT = prompt = """
Your task is:
Explain the code.
Following the task requirements, explain the selected portion of the code. \
Here is the relevant context \
information for your reference:
1.  selected code info: {selected_text}
2.  current visible code info: {visible_text}
"""

EXPLAIN_PROMPT_ZH = prompt = """
你的任务是：
解释代码。
根据任务要求，解释被选中部分的代码。你可以参考的 context 有：
1. 编辑器中被选中的代码：{selected_text}
2. 当前编辑器中可见代码：{visible_text}
"""


def get_prompt():
    ide_language = IDEService().ide_language()
    return EXPLAIN_PROMPT_ZH if ide_language == "zh" else EXPLAIN_PROMPT


@chat(prompt=get_prompt(), stream_out=True)
# pylint: disable=unused-argument
def explain(selected_text, visible_text):
    """
    call ai to explain selected code
    """
    pass  # pylint: disable=unnecessary-pass


def main():
    explain(selected_text=get_selected_code(), visible_text=get_visible_code())
    sys.exit(0)


if __name__ == "__main__":
    main()
