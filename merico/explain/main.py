import sys

from devchat.llm import chat

from lib.ide_service import IDEService
from lib.workflow.decorators import check_select_code


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
Note that you only explain the logic of the selected code. \
The visible code only serves as the context for you to understand the code. \
Here is the relevant context \
information for your reference:
1.  selected code info: {selected_text}
2.  current visible code info: {visible_text}
"""

EXPLAIN_PROMPT_ZH = prompt = """
你的任务是：
使用中文解释代码。
根据任务要求，解释被选中部分的代码。注意只解释被选中的代码逻辑，\
可见代码只是作为你理解代码的 context，你可以参考的 context 有：
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


@check_select_code("Please select code to explain.")
def main(code: dict):
    result = explain(selected_text=code["text"], visible_text=get_visible_code())
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
