from typing import List

from .iobase import pipe_interaction


class CheckboxOption:
    def __init__(self, id, text, group: str = None, checked: bool = False):
        # it will show as: [] (id): text
        self._id = id
        self._text = text
        self._group = group
        self._checked = checked


def make_checkbox_control(title: str, options: List[CheckboxOption]) -> (str, str, List[str]):
    _NT = "\n"
    groups = list({option._group: 1 for option in options if option._group}.keys())

    def _check_option_message(option):
        return f"> [{'x' if option._checked else ''}]({option._id}) {option._text}"

    def _check_option_group_message(group):
        s = _NT.join(
            [_check_option_message(option) for option in options if option._group == group]
        )
        return f"{group}:{_NT}{s}"

    ui_message = f"""
{title}
{_NT.join([_check_option_group_message(group) for group in groups])}
    """
    return ("checkbox", ui_message, [option._id for option in options])


def checkbox_answer(response: dict, ids: List[str]) -> List[str]:
    return [key for key, value in response.items() if value == "checked" and key in ids]


def ui_checkbox_select(title: str, options: List[CheckboxOption]) -> List[str]:
    """
    send text to UI as:
    ```chatmark
    Which files would you like to commit? I've suggested a few.
    > [x](file1) devchat/engine/prompter.py
    > [x](file2) devchat/prompt.py
    > [](file3) tests/test_cli_prompt.py
    ```
    """
    _1, ui_message, ids = make_checkbox_control(title, options)
    ui_message = f"""```chatmark type=form\n{ui_message}\n```\n"""

    # print(ui_message)
    # return [option._id for option in options]
    response = pipe_interaction(ui_message)
    return checkbox_answer(response, ids)
