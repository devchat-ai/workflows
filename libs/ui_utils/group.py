from typing import List, Tuple

from .iobase import pipe_interaction
from .multi_selections import checkbox_answer
from .single_select import radio_answer
from .text_edit import editor_answer


def ui_group(ui_message: List[Tuple]) -> Tuple:
    """
    ui_message: List[Tuple]
        [
            ("editor", "editor ui message", "editor_id"),
            ("checkbox", "checkbox ui message", ["id1", "id2"]),
            ("radio", "radio ui message", ["id1", "id2"]),
        ]

    items in ui_message are created by functions like:make_checkbox_control
    """
    ui_message_str = "\n".join([m[1] for m in ui_message])

    ui_message_str = f"""```chatmark type=form\n{ui_message_str}\n```\n"""
    response = pipe_interaction(ui_message_str)

    results = []
    for m in ui_message:
        if m[0] == "editor":
            result = editor_answer(response, m[2])
        elif m[0] == "checkbox":
            result = checkbox_answer(response, m[2])
        elif m[0] == "radio":
            result = radio_answer(response, m[2])
        else:
            result = None
        results.append(result)
    return tuple(results)
