import os
import sys
import re
import json

home = os.path.expanduser("~")
org_libs_path = os.path.join(home, ".chat", "workflows", "org", "libs")
sys_libs_path = os.path.join(home, ".chat", "workflows", "sys", "libs")
sys.path.append(org_libs_path)
sys.path.append(sys_libs_path)

from llm_api import chat_completion_stream  # noqa: E402
from ide_services.services import visible_lines, selected_lines, diff_apply  # noqa: E402


def create_prompt():
    question = sys.argv[1]

    visible_data = visible_lines()
    selected_data = selected_lines()

    file_path = visible_data["filePath"]
    if not os.path.exists(file_path):
        print("Current file is not valid filename:", file_path, file=sys.stderr, flush=True)
        sys.exit(-1)

    if selected_data["selectedText"] == "":
        print("Please select some text.", file=sys.stderr, flush=True)
        sys.exit(-1)

    prompt = f"""
    你的任务是:
    {question}
    根据任务要求，仅修改选中的代码部分。请确保修改后的代码段与选中的代码保持相同的缩进，\
    以便与现有的代码结构无缝集成并保持正确的语法。只重构选中的代码。保留所有其他信息。\
    以下是您参考的相关上下文信息：
    1.  选中代码信息: {selected_data}
    2.  可视窗口代码信息: {visible_data}
    """
    return prompt


def extract_markdown_block(text):
    """
    Extracts the first Markdown code block from the given text without the language specifier.

    :param text: A string containing Markdown text
    :return: The content of the first Markdown code block, or None if not found
    """
    # 正则表达式匹配Markdown代码块，忽略可选的语言类型标记
    pattern = r"```(?:\w+)?\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # 返回第一个匹配的代码块内容，去除首尾的反引号和语言类型标记
        # 去除块结束标记前的一个换行符，但保留其他内容
        block_content = match.group(1)
        return block_content
    else:
        # 如果没有找到匹配项，返回None
        return text


def replace_selected(new_code):
    selected_data = selected_lines()
    select_file = selected_data["filePath"]
    select_range = selected_data["selectedRange"]  # [start_line, start_col, end_line, end_col]

    # Read the file
    with open(select_file, "r") as file:
        lines = file.readlines()
    lines.append("\n")

    # Modify the selected lines
    start_line, start_col, end_line, end_col = select_range

    # If the selection spans multiple lines, handle the last line and delete the lines in between
    if start_line != end_line:
        lines[start_line] = lines[start_line][:start_col] + new_code
        # Append the text after the selection on the last line
        lines[start_line] += lines[end_line][end_col:]
        # Delete the lines between start_line and end_line
        del lines[start_line + 1 : end_line + 1]
    else:
        # If the selection is within a single line, remove the selected text
        lines[start_line] = lines[start_line][:start_col] + new_code + lines[end_line][end_col:]

    # Combine everything back together
    modified_text = "".join(lines)

    # Write the changes back to the file
    with open(select_file, "w") as file:
        file.write(modified_text)


def main():
    # messages = json.loads(
    #     os.environ.get("CONTEXT_CONTENTS", json.dumps([{"role": "user", "content": ""}]))
    # )
    messages = [{"role": "user", "content": create_prompt()}]

    response = chat_completion_stream(messages, {"model": os.environ.get("LLM_MODEL", "gpt-3.5-turbo-1106")}, stream_out=True)
    if not response:
        sys.exit(-1)
    print("\n")
    new_code = extract_markdown_block(response["content"])
    # Check if new_code is empty and handle the case appropriately
    if not new_code:
        print("Parsing result failed. Exiting with error code -1", file=sys.stderr)
        sys.exit(-1)

    # replace_selected(new_code)
    selected_data = selected_lines()
    select_file = selected_data["filePath"]
    diff_apply("", new_code)
    # print(response["content"], flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
    # print("hello")
