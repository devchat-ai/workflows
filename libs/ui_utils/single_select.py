from typing import List

from .iobase import pipe_interaction


class RadioOption:
    def __init__(self, id, text):
        # it will show as: - (id): text
        self._id = id
        self._text = text


def make_radio_control(title: str, options: List[RadioOption]) -> (str, str, List[str]):
    def _option_line(option):
        return f"> - ({option._id}) {option._text}"

    options_lines = "\n".join([_option_line(option) for option in options])
    ui_message = f"""
{title}
{options_lines}
"""
    return ('radio', ui_message, [option._id for option in options])


def radio_answer(response: dict, ids: List[str]) -> str | None:
    selected_options = [key for key, value in response.items() if value == "checked" and key in ids]
    return selected_options[0] if selected_options else None


def ui_radio_select(title: str, options: List[RadioOption]) -> str | None:
    """
    ```chatmark type=form
        How would you like to make the change?
        > - (insert) Insert the new code.
        > - (new) Put the code in a new file.
        > - (replace) Replace the current code.
        ```
    """
    _1, ui_message, ids = make_radio_control(title, options)
    ui_message = f"""```chatmark type=form\n{ui_message}\n```\n"""
    response = pipe_interaction(ui_message)
    return radio_answer(response, ids)
