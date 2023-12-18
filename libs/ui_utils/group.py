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
    """
    ui_message = "\n".join([m[1] for m in ui_message])
    with open('tmp.txt', 'w+', encoding="utf8") as file:
        file.write(ui_message)
    response = pipe_interaction(ui_message)
    return tuple([
        editor_answer(response, m[2]) if m[0] == "editor" else
        checkbox_answer(response, m[2]) if m[0] == "checkbox" else
        radio_answer(response, m[2]) if m[0] == "radio" else
        None
        for m in ui_message
    ])
