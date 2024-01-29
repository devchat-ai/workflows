import os
import sys
from typing import List, Tuple

import click

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))

from chatmark import Checkbox, Form, Step, TextEditor  # noqa: E402
from find_reference_tests import find_reference_tests
from i18n import TUILanguage, get_translation
from ide_services import ide_language  # noqa: E402
from model import (
    FuncToTest,
    TokenBudgetExceededException,
    UserCancelledException,
)
from propose_test import propose_test
from tools.file_util import retrieve_file_content
from write_tests import write_and_print_tests


class UnitTestsWorkflow:
    def __init__(
        self,
        user_prompt: str,
        func_to_test: FuncToTest,
        repo_root: str,
        tui_lang: TUILanguage,
    ):
        self.user_prompt = user_prompt
        self.func_to_test = func_to_test
        self.repo_root = repo_root
        self.tui_lang = tui_lang

    def run(self):
        """
        Run the workflow to generate unit tests.
        """
        cases, files = self.step1_propose_cases_and_reference_files()

        cases, files = self.step2_edit_cases_and_reference_files(cases, files)

        self.step3_write_and_print_tests(cases, files)

    def step1_propose_cases_and_reference_files(
        self,
    ) -> Tuple[List[str], List[str]]:
        """
        Propose test cases and reference files for a specified function.

        Return: (test_cases, reference_files)
        """
        test_cases: List[str] = []
        reference_files: List[str] = []

        _i = get_translation(self.tui_lang)

        msg = _i("Analyzing the function and current unit tests...")

        with Step(msg):
            test_cases = propose_test(
                user_prompt=self.user_prompt,
                func_to_test=self.func_to_test,
                chat_language=self.tui_lang.chat_language,
            )

            ref_files = find_reference_tests(
                self.repo_root,
                self.func_to_test.func_name,
                self.func_to_test.file_path,
            )

        if ref_files:
            # Only use the most relevant reference file currently
            reference_files.append(ref_files[0])

        return test_cases, reference_files

    def step2_edit_cases_and_reference_files(
        self, test_cases: List[str], reference_files: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Edit test cases and reference files by user.

        Return the updated cases and valid reference files.
        """
        _i = get_translation(self.tui_lang)

        checkbox = Checkbox(
            options=test_cases,
            title=_i("Select test cases to generate"),
        )
        case_editor = TextEditor(
            text="",
            title=_i(
                "You can add more test cases here\n"
                "(Multiple cases can be separated by line breaks)"
            ),
        )
        ref_editor = TextEditor(
            text=reference_files[0] if reference_files else "",
            title=_i("Edit reference test file\n(Multiple files can be separated by line breaks)"),
        )

        form = Form(components=[checkbox, case_editor, ref_editor])
        form.render()

        # Check test cases
        cases = [checkbox.options[idx] for idx in checkbox.selections]
        user_cases = []
        if case_editor.new_text:
            user_cases = [c.strip() for c in case_editor.new_text.split("\n")]
            user_cases = [c for c in user_cases if c]

        cases.extend(user_cases)

        # Check if any test case is selected
        if not cases:
            raise UserCancelledException(_i("No test case is selected. Quit generating tests."))

        # Validate reference files
        ref_files = [f.strip() for f in ref_editor.new_text.split("\n")]
        valid_files = []
        invalid_files = []

        for ref_file in ref_files:
            if not ref_file:
                continue
            try:
                retrieve_file_content(file_path=ref_file, root_path=self.repo_root)
                valid_files.append(ref_file)
            except Exception:
                invalid_files.append(ref_file)

        # Print summary
        title = _i("Will generate tests for the following cases.")
        lines = []

        lines.append(_i("\nTest cases:"))
        width = len(str(len(cases)))
        lines.extend([f"{(i+1):>{width}}. {c}" for i, c in enumerate(cases)])

        if not valid_files:
            lines.append(
                _i(
                    "\nNo valid reference file is provided. "
                    "Will not use reference to generate tests."
                )
            )
        else:
            lines.append(_i("\nWill use the following reference files to generate tests."))
            lines.append(_i("\nValid reference files:"))
            width = len(str(len(valid_files)))
            lines.extend([f"{(i+1):>{width}}. {f}" for i, f in enumerate(valid_files)])

        if invalid_files:
            lines.append(_i("\nInvalid files:"))
            width = len(str(len(invalid_files)))
            lines.extend([f"{(i+1):>{width}}. {f}" for i, f in enumerate(invalid_files)])

        with Step(title):
            print("\n".join(lines), flush=True)

        return cases, valid_files

    def step3_write_and_print_tests(
        self,
        cases: List[str],
        ref_files: List[str],
    ):
        """
        Write and print tests.
        """

        write_and_print_tests(
            root_path=self.repo_root,
            func_to_test=self.func_to_test,
            test_cases=cases,
            reference_files=ref_files,
            chat_language=self.tui_lang.chat_language,
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
        workflow = UnitTestsWorkflow(user_prompt, func_to_test, repo_root, tui_lang)
        workflow.run()

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
