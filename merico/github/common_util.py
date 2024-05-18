
import functools
import sys
import os


from lib.chatmark import TextEditor, Form, Radio, Checkbox


def create_ui_objs(ui_decls, args):
    ui_objs = []
    editors = []
    for i, ui in enumerate(ui_decls):
        editor = ui[0](args[i])
        if ui[1]:
            # this is the title of UI object
            editors.append(ui[1])
        editors.append(editor)
        ui_objs.append(editor)
    return ui_objs, editors


def edit_form(uis, args):
    ui_objs, editors = create_ui_objs(uis, args)
    form = Form(editors)
    form.render()
    
    values = []
    for obj in ui_objs:
        if isinstance(obj, TextEditor):
            values.append(obj.new_text)
        elif isinstance(obj, Radio):
            values.append(obj.selection)
        else:
            # TODO
            pass
    return values
    

def editor(description):
    def decorator_edit(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            uis = wrapper.uis[::-1]
            return edit_form(uis, args)
        
        if hasattr(func, "uis"):
            wrapper.uis = func.uis
        else:
            wrapper.uis = []
        wrapper.uis.append((TextEditor, description))
        return wrapper
    return decorator_edit

def ui_edit(ui_type, description):
    def decorator_edit(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            uis = wrapper.uis[::-1]
            return edit_form(uis, args)
        
        if hasattr(func, "uis"):
            wrapper.uis = func.uis
        else:
            wrapper.uis = []
        ui_type_class = {
            "editor": TextEditor,
            "radio": Radio,
            "checkbox": Checkbox
        }[ui_type]
        wrapper.uis.append((ui_type_class, description))
        return wrapper
    return decorator_edit

def assert_exit(condition, message, exit_code = -1):
    if condition:
        if exit_code == 0:
            print(message, end="\n\n", flush=True)
        else:
            print(message, end="\n\n", file=sys.stderr, flush=True)
        sys.exit(exit_code)