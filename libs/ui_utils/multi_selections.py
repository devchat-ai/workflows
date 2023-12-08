from typing import List

from .iobase import pipe_interaction


class CheckboxOption:
    def __init__(self, id, text, group: str = None, checked: bool = False):
        # it will show as: [] (id): text
        self._id = id
        self._text = text
        self._group = group
        self._checked = checked


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
    _NT = "\n"
    groups = list({option._group: 1 for option in options if option._group}.keys())
    check_option_message = (
        lambda option: f"> [{'x' if option._checked else ''}]({option._id}) {option._text}"
    )
    check_option_group_message = (
        lambda group: f"{group}:{_NT}{_NT.join([check_option_message(option) for option in options if option._group==group])}"
    )
    ui_message = f"""
```chatmark type=form
{title}
{_NT.join([check_option_group_message(group) for group in groups])}
```
    """
    # print(ui_message)
    # return [option._id for option in options]
    response = pipe_interaction(ui_message)

    selected_options = [
        key
        for key, value in response.items()
        if value == "checked" and key in [option._id for option in options]
    ]
    return selected_options
