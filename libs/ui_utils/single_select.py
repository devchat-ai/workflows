from typing import List

from .iobase import pipe_interaction


class RadioOption:
    def __init__(self, id, text):
        # it will show as: - (id): text
        self._id = id
        self._text = text


def ui_radio_select(title: str, options: List[RadioOption]) -> str | None:
    """
    ```chatmark type=form
        How would you like to make the change?
        > - (insert) Insert the new code.
        > - (new) Put the code in a new file.
        > - (replace) Replace the current code.
        ```
    """
    option_line = lambda option: f"> - ({option._id}) {option._text}"
    options_lines = "\n".join([option_line(option) for option in options])
    ui_message = f"""
```chatmark type=form
{title}
{options_lines}
```
"""

    response = pipe_interaction(ui_message)

    selected_options = [
        key
        for key, value in response.items()
        if value == "checked" and key in [option._id for option in options]
    ]
    return selected_options[0] if len(selected_options) > 0 else None
