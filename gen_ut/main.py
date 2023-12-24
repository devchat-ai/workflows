from typing import Optional, Dict
import os
import sys
import click
import time

from propose_test import propose_test
from find_reference_tests import find_reference_tests
from write_tests import write_and_print_tests
from chat.ask_codebase.tools.retrieve_file_content import retrieve_file_content
from i18n import TUILanguage, get_translation


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "libs"))

from ui_utils import ui_checkbox_select, ui_text_edit, CheckboxOption  # noqa: E402
from ide_services import ide_language  # noqa: E402


def _get_relevant_content(
    repo_root: str,
    file_path: str,
    function_name: str,
    start_line: Optional[int] = None,  # 0-based, inclusive
    end_line: Optional[int] = None,  # 0-based, inclusive
) -> str:
    """
    Get the relevant content for a function.

    it can be the whole file, or the specified lines of the file.
    """
    file_content = retrieve_file_content(file_path, repo_root)

    func_content = file_content

    if start_line is not None and end_line is not None:
        lines = file_content.split("\n")
        func_content = "\n".join(lines[start_line : end_line + 1])

    return func_content


@click.command()
@click.argument("user_prompt", required=True)
@click.option("-fn", "--func_name", required=True, type=str)
@click.option("-fp", "--file_path", required=True, type=str)
@click.option("-sln", "--start_line", required=False, type=int)
@click.option("-eln", "--end_line", required=False, type=int)
def main(
    user_prompt: str,
    func_name: str,
    file_path: str,
    start_line: Optional[int],  # 0-based, inclusive
    end_line: Optional[int],  # 0-based, inclusive
):
    repo_root = os.getcwd()
    tui_lang = TUILanguage.from_str(ide_language())
    # tui_lang = TUILanguage.from_str("zh")
    _i = get_translation(tui_lang)

    # Use relative path in inner logic
    if os.path.isabs(file_path):
        file_path = os.path.relpath(file_path, repo_root)

    print("\n\n$$$$$$$$$$$\n\n")
    print(f"repo_root: {repo_root}\n\n")
    print(f"user_prompt: {user_prompt}\n\n")
    print(f"func_name: {func_name}\n\n")
    print(f"file_path: {file_path}\n\n")
    print(f"start_line: {start_line}\n\n")
    print(f"end_line: {end_line}\n\n")
    print(f"tui_lang: {tui_lang}, {tui_lang.language_code}, { tui_lang.chat_language}\n\n")
    print(_i("hello"))
    print("\n\n$$$$$$$$$$$\n\n", flush=True)

    print(
        _i("\n\n```Step\n# Analyzing the function and current unit tests...\n"),
        flush=True,
    )

    relevant_content = _get_relevant_content(
        repo_root=repo_root,
        file_path=file_path,
        function_name=func_name,
        start_line=start_line,
        end_line=end_line,
    )

    test_cases = propose_test(
        repo_root=repo_root,
        user_prompt=user_prompt,
        function_name=func_name,
        function_content=relevant_content,
        file_path=file_path,
        chat_language=tui_lang.chat_language,
    )
    ref_files = find_reference_tests(repo_root, func_name, file_path)
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

    # tmp sleep to show some issues in demo
    time.sleep(1)

    selected_cases = [case_id_to_option[id]._text for id in selected_ids]

    ref_file = ref_files[0] if ref_files else ""
    new_ref_file = ui_text_edit(_i("Edit reference test file"), ref_file)

    # tmp sleep to show some issues in demo
    time.sleep(1)

    write_and_print_tests(
        root_path=repo_root,
        function_name=func_name,
        function_content=relevant_content,
        file_path=file_path,
        test_cases=selected_cases,
        reference_files=[new_ref_file] if new_ref_file else None,
        chat_language=tui_lang.chat_language,
    )


if __name__ == "__main__":
    main()
