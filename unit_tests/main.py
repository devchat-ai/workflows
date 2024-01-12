import os
import sys

import click
from chat.ask_codebase.tools.retrieve_file_content import retrieve_file_content
from find_reference_tests import find_reference_tests
from i18n import TUILanguage, get_translation
from model import FuncToTest, TokenBudgetExceededException, UserCancelledException
from propose_test import propose_test
from write_tests import write_and_print_tests

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))

from chatmark import Checkbox, Form, Step, TextEditor  # noqa: E402
from ide_services import ide_language  # noqa: E402


def generate_unit_tests_workflow(
    user_prompt: str,
    func_to_test: FuncToTest,
    tui_lang: TUILanguage,
):
    """
    The main workflow for generating unit tests.
    """
    repo_root = os.getcwd()

    _i = get_translation(tui_lang)

    msg = _i("Analyzing the function and current unit tests...")

    with Step(msg):
        test_cases = propose_test(
            user_prompt=user_prompt,
            func_to_test=func_to_test,
            chat_language=tui_lang.chat_language,
        )

        ref_files = find_reference_tests(repo_root, func_to_test.func_name, func_to_test.file_path)

    ref_file = ref_files[0] if ref_files else ""

    cases_checkbox = Checkbox(
        options=test_cases,
        title=_i("Select test cases to generate"),
    )
    ref_file_editor = TextEditor(
        text=ref_file,
        title=_i("Edit reference test file\n(Multiple files can be separated by line breaks)"),
    )

    form = Form(components=[cases_checkbox, ref_file_editor])
    form.render()

    selected_cases = [cases_checkbox.options[idx] for idx in cases_checkbox.selections]
    new_refs = ref_file_editor.new_text

    # Check user input
    # Check if any test case is selected
    if not cases_checkbox.selections:
        raise UserCancelledException(_i("No test case is selected. Quit generating tests."))

    # Validate reference files
    valid_files = []
    invalid_files = []
    ref_files = [f.strip() for f in new_refs.split("\n")]

    for ref_file in ref_files:
        if not ref_file:
            continue
        try:
            retrieve_file_content(file_path=ref_file, root_path=repo_root)
            valid_files.append(ref_file)

        except Exception as e:
            invalid_files.append(ref_file)

    title = ""
    lines = []
    if not valid_files:
        title = _i("No valid file is provided. Will not use reference to generate tests.")
    else:
        title = _i("Will use the following reference files to generate tests:")
        lines.append(_i("\nValid reference files:"))
        lines.extend(valid_files)

    if invalid_files:
        lines.append(_i("\nInvalid files:"))
        lines.extend(invalid_files)

    with Step(title):
        print("\n".join(lines), flush=True)

    write_and_print_tests(
        root_path=repo_root,
        func_to_test=func_to_test,
        test_cases=selected_cases,
        reference_files=valid_files,
        chat_language=tui_lang.chat_language,
    )


@click.command()
@click.argument("input", required=True)
def main(input: str):
    """
    The main entry point for the unit tests generation workflow.
    "/unit_tests {a}:::{b}:::{c}:::{d}:::{e}:::{f}"
    """
    # Parse input
    params = input.strip().split(":::")
    assert len(params) == 6, f"Invalid input: {input}, number of params: {len(params)}"

    (
        file_path,
        func_name,
        func_start_line,  # 0-based, inclusive
        func_end_line,  # 0-based, inclusive
        container_start_line,  # 0-based, inclusive
        container_end_line,  # 0-based, inclusive
    ) = params

    try:
        func_start_line = int(func_start_line)
        func_end_line = int(func_end_line)
        container_start_line = int(container_start_line)
        container_end_line = int(container_end_line)
    except Exception as e:
        raise Exception(f"Invalid input: {input}, error: {e}")

    user_prompt = f"Help me write unit tests for the `{func_name}` function"

    repo_root = os.getcwd()
    ide_lang = ide_language()
    tui_lang = TUILanguage.from_str(ide_lang)
    _i = get_translation(tui_lang)

    # Use relative path in inner logic
    if os.path.isabs(file_path):
        file_path = os.path.relpath(file_path, repo_root)

    func_to_test = FuncToTest(
        func_name=func_name,
        repo_root=repo_root,
        file_path=file_path,
        func_start_line=func_start_line,
        func_end_line=func_end_line,
        container_start_line=container_start_line,
        container_end_line=container_end_line,
    )

    try:
        generate_unit_tests_workflow(user_prompt, func_to_test, tui_lang)

    except TokenBudgetExceededException as e:
        msg = _i("The function's size surpasses AI's context capacity.")

        with Step(msg):
            print(f"\n{e}\n", flush=True)

    except UserCancelledException as e:
        with Step(f"{e}"):
            pass

    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
