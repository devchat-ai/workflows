import os
import re
import sys

from devchat.llm import chat

from lib.ide_service import IDEService


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


REWRITE_PROMPT = prompt = """
Your task is:
{question}
Following the task requirements, modify only the selected portion of the code. \
Please ensure that the revised code segment maintains the same indentation as the \
selected code to seamlessly integrate with the existing code structure and maintain \
correct syntax. Just refactor the selected code. Keep all other information as it is. \
Here is the relevant context \
information for your reference:
1.  selected code info: {selected_text}
2.  current visible code info: {visible_text}
"""


@chat(prompt=REWRITE_PROMPT, stream_out=True)
# pylint: disable=unused-argument
def ai_rewrite(question, selected_text, visible_text):
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


def replace_selected(new_code):
    selected_data = IDEService().get_selected_code().dict()
    select_file = selected_data["abspath"]
    select_range = selected_data["range"]  # [start_line, start_col, end_line, end_col]

    # Read the file
    with open(select_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    lines.append("\n")

    # Modify the selected lines
    start_line = select_range["start"]["line"]
    start_col = select_range["start"]["character"]
    end_line = select_range["end"]["line"]
    end_col = select_range["end"]["character"]

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
    with open(select_file, "w", encoding="utf-8") as file:
        file.write(modified_text)


def main():
    question = sys.argv[1]
    # prepare code
    selected_text = get_selected_code()
    visible_text = get_visible_code()

    # rewrite
    response = ai_rewrite(question=question, selected_text=selected_text, visible_text=visible_text)

    # apply new code to editor
    new_code = extract_markdown_block(response)
    IDEService().diff_apply("", new_code)

    sys.exit(0)


if __name__ == "__main__":
    main()
