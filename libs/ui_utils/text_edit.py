from typing import Optional
from .iobase import pipe_interaction


def make_editor_control(editor_id: str, title: str, text: str) -> (str, str, str):
    text_lines = text.strip().split("\n")
    if len(text_lines) > 0 and text_lines[0].strip().startswith("```"):
        text_lines = text_lines[1:]
    if len(text_lines) > 0 and text_lines[-1].strip() == "```":
        text_lines = text_lines[:-1]
    text = "\n".join(text_lines)
    text = text.replace("\n", "\n> ")
    ui_message = f"""
{title}

> | ({editor_id})
> {text}
"""
    return ("editor", ui_message, editor_id)


def editor_answer(response: dict, editor_id: str) -> Optional[str]:
    if editor_id in response:
        return response[editor_id]
    return None


def ui_text_edit(title: str, text: str) -> Optional[str]:
    """
    ```chatmark type=form
    I've drafted a commit message for you as below. Feel free to modify it.

    > | (ID)
    > fix: prevent racing of requests
    >
    > Introduce a request id and a reference to latest request. Dismiss
    > incoming responses other than from latest request.
    >
    > Reviewed-by: Z
    > Refs: #123
    ```
    """
    _1, ui_message, editor_id = make_editor_control("editor0", title, text)
    ui_message = f"""```chatmark type=form\n{ui_message}\n```\n"""
    response = pipe_interaction(ui_message)
    return editor_answer(response, editor_id)
