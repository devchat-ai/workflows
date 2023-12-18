from typing import Optional, List, Dict
import os
import sys
import click

from propose_test import propose_test
from find_reference_tests import find_reference_tests
from write_tests import write_tests


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "libs"))

from ui_utils import ui_checkbox_select, ui_text_edit, CheckboxOption

from pprint import pprint



@click.command()
@click.argument("user_prompt", required=True)
@click.option("-fn", "--function_name", required=True, type=str)
@click.option("-fp", "--file_path", required=True, type=str)
@click.option("-sln", "--start_line", required=False, type=int)
@click.option("-eln", "--end_line", required=False, type=int)
def main(
    user_prompt: str,
    function_name: str,
    file_path: str,
    start_line: Optional[int],  # 0-based
    end_line: Optional[int],  # 0-based
):
    repo_root = os.getcwd()
    print("\n\n$$$$$$$$$$$\n\n")
    print(f"repo_root: {repo_root}\n\n")
    print(f"user_prompt: {user_prompt}\n\n")
    print(f"function_name: {function_name}\n\n")
    print(f"file_path: {file_path}\n\n")
    print(f"start_line: {start_line}\n\n")
    print(f"end_line: {end_line}\n\n")
    print("\n\n$$$$$$$$$$$\n\n", flush=True)

    print(
        "\n\n```Step\n# Analyzing the function and current unit tests...\n",
        flush=True,
    )

    test_cases = propose_test(
        repo_root=repo_root,
        user_prompt=user_prompt,
        function_name=function_name,
        file_path=file_path,
    )
    ref_files = find_reference_tests(repo_root, function_name, file_path)
    print("Complete analyzing.\n```", flush=True)

    # print("\n\n$$$$$$$$$$$\n\n")
    # pprint(test_cases)
    # print(type(test_cases), len(test_cases))
    # print("\n\n##########\n\n", flush=True)

    case_id_to_option: Dict[str, CheckboxOption] = {
        f"case_{i}": CheckboxOption(
            id=f"case_{i}", text=desc, group="proposed cases", checked=False
        )
        for i, desc in enumerate(test_cases)
    }

    selected_ids = ui_checkbox_select(
        "Select test cases to generate", list(case_id_to_option.values())
    )
    selected_cases = [case_id_to_option[id]._text for id in selected_ids]

    # print("\n\n$$$$$$$$$$$\n\n")
    # pprint(selected_ids)
    # print(type(selected_ids), len(selected_ids))
    # pprint(selected_cases)
    # print("\n\n##########\n\n", flush=True)

    ref_file = ref_files[0] if ref_files else ""
    new_ref_file = ui_text_edit("Edit reference test file", ref_file)

    # print("\n\n$$$$$$$$$$$\n\n")
    # pprint(new_ref_file)
    # print(type(new_ref_file), len(new_ref_file))
    # print("\n\n##########\n\n", flush=True)

    print(
        "\n\n```Step\n# Generating tests...\n",
        flush=True,
    )
    generated = write_tests(
        root_path=repo_root,
        function_name=function_name,
        file_path=file_path,
        test_cases=selected_cases,
        reference_files=[new_ref_file] if new_ref_file else None,
    )
    print("Complete Generating.\n```", flush=True)

    # print("\n\n$$$$$$$$$$$\n\n")
    # print(generated)
    # print(type(generated))
    # print("\n\n##########\n\n", flush=True)
    print(generated, flush=True)


if __name__ == "__main__":
    main()


"""
~/.chat/mamba/envs/devchat-commands/bin/python main.py \
    "help me write test cases for propose_tests function" \
    -fn propose_tests \
    -fp chat/ask_codebase/assistants/propose_tests.py
"""
