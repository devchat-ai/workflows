from typing import Optional, Dict
import os
import sys
import click

from propose_test import propose_test
from find_reference_tests import find_reference_tests
from write_tests import write_and_print_tests
from i18n import TUILanguage, get_translation

from model import FuncToTest, TokenBudgetExceededException

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))

from ui_utils import ui_checkbox_select, ui_text_edit, CheckboxOption  # noqa: E402
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

    print(
        _i("\n\n```Step\n# Analyzing the function and current unit tests...\n"),
        flush=True,
    )

    test_cases = propose_test(
        user_prompt=user_prompt,
        func_to_test=func_to_test,
        chat_language=tui_lang.chat_language,
    )

    ref_files = find_reference_tests(repo_root, func_to_test.func_name, func_to_test.file_path)
    print(_i("Complete analyzing.\n```"), flush=True)

    case_id_to_option: Dict[str, CheckboxOption] = {
        f"case_{i}": CheckboxOption(
            id=f"case_{i}", text=desc, group=_i("proposed cases"), checked=False
        )
        for i, desc in enumerate(test_cases)
    }

    selected_ids = ui_checkbox_select(
        _i("Select test cases to generate"), list(case_id_to_option.values())
    )

    selected_cases = [case_id_to_option[id]._text for id in selected_ids]

    ref_file = ref_files[0] if ref_files else ""
    new_ref_file = ui_text_edit(_i("Edit reference test file"), ref_file)

    write_and_print_tests(
        root_path=repo_root,
        func_to_test=func_to_test,
        test_cases=selected_cases,
        reference_files=[new_ref_file] if new_ref_file else None,
        chat_language=tui_lang.chat_language,
    )


@click.command()
@click.argument("user_prompt", required=True)
@click.option("-fn", "--func_name", required=True, type=str)
@click.option("-fp", "--file_path", required=True, type=str)
@click.option("-fsl", "--func_start_line", required=True, type=int)
@click.option("-fel", "--func_end_line", required=True, type=int)
# Optional container_name is not well supported in Shortcut button's variable
# @click.option("-cn", "--container_name", required=False, type=str)
@click.option("-csl", "--container_start_line", required=False, type=int)
@click.option("-cel", "--container_end_line", required=False, type=int)
def main(
    user_prompt: str,
    func_name: str,
    file_path: str,
    func_start_line: Optional[int],  # 0-based, inclusive
    func_end_line: Optional[int],  # 0-based, inclusive
    container_start_line: Optional[int],  # 0-based, inclusive
    container_end_line: Optional[int],  # 0-based, inclusive
):
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

    print("\n\n$$$$$$$$$$$\n\n")
    print(f"repo_root: {repo_root}\n\n")
    print(f"user_prompt: {user_prompt}\n\n")
    print(f"func_name: {func_name}\n\n")
    print(func_to_test, "\n\n")
    print("func_content: \n\n")
    print("```")
    print(func_to_test.func_content)
    print("```")
    print("container_content: \n\n")
    print("```")
    print(func_to_test.container_content)
    print("```")
    print(f"ide_lang: {ide_lang}\n\n")
    print(f"tui_lang: {tui_lang}, {tui_lang.language_code}, { tui_lang.chat_language}\n\n")
    print(_i("hello"))
    print("\n\n$$$$$$$$$$$\n\n", flush=True)

    try:
        generate_unit_tests_workflow(user_prompt, func_to_test, tui_lang)

    except TokenBudgetExceededException as e:
        print(
            f"Funciton {func_to_test.func_name} is too large for AI to handle.",
            flush=True,
        )
        print(e, flush=True)
    except Exception as e:
        print(e, file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
