# 在 ask/command.py 中
import os
import sys

from devchat.llm import chat

from lib.ide_service import IDEService

ROOT_WORKFLOW_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_WORKFLOW_DIR)

from chatflow.util.contexts import CONTEXTS  # noqa: E402

PROMPT = (
    f"""
{CONTEXTS.replace("{", "{{").replace("}", "}}")}
"""
    + """
当前选中代码：{selected_code}
当前打开文件路径：{file_path}
用户要求或问题：{question}
"""
)


@chat(prompt=PROMPT, stream_out=True)
def ask(question, selected_code, file_path):
    pass


def get_selected_code():
    """Retrieves the selected lines of code from the user's selection."""
    selected_data = IDEService().get_selected_range().dict()
    return selected_data


def main(question):
    selected_text = get_selected_code()
    file_path = selected_text.get("abspath", "")
    code_text = selected_text.get("text", "")

    ask(question=question, selected_code=code_text, file_path=file_path)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1])
