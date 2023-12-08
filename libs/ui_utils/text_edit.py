import os
from typing import List

from .iobase import pipe_interaction


def ui_text_edit(title: str, text: str) -> str | None:
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
    text_lines = text.strip().split("\n")
    if len(text_lines) > 0 and text_lines[0].strip().startswith("```"):
        text_lines = text_lines[1:]
    if len(text_lines) > 0 and text_lines[-1].strip() == "```":
        text_lines = text_lines[:-1]
    text = "\n".join(text_lines)
    text = text.replace("\n", "\n> ")
    ui_message = f"""
```chatmark type=form
{title}

> | (editor0)
> {text}
```
"""
    response = pipe_interaction(ui_message)
    if "editor0" in response:
        return response["editor0"]
    return None
