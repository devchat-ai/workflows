import os
from typing import Dict, List, Tuple

import click
from cache import LocalCache
from find_context import (
    Context,
    Position,
    Range,
    find_symbol_context_by_static_analysis,
    find_symbol_context_of_llm_recommendation,
)
from find_reference_tests import find_reference_tests
from i18n import TUILanguage, get_translation
from model import (
    FuncToTest,
    TokenBudgetExceededException,
    UserCancelledException,
)
from propose_test import propose_test
from tools.file_util import retrieve_file_content
from write_tests import write_and_print_tests

from lib.chatmark import Checkbox, Form, Step, TextEditor
from lib.ide_service import IDEService

CHAT_WORKFLOW_DIR_PATH = [".chat", "workflows"]


class UnitTestsWorkflow:
    def __init__(
        self,
        user_prompt: str,
        func_to_test: FuncToTest,
        repo_root: str,
        tui_lang: TUILanguage,
        local_cache: LocalCache,
    ):
        self.user_prompt = user_prompt
        self.func_to_test = func_to_test
        self.repo_root = repo_root
        self.tui_lang = tui_lang
        self.local_cache = local_cache

    def run(self):
        """
        Run the workflow to generate unit tests.
        """
        symbol_context = self.step1_find_symbol_context()
        contexts = set()
        for _, v in symbol_context.items():
            contexts.update(v)
        contexts = list(contexts)

        cases, files = self.step2_propose_cases_and_reference_files(contexts)

        res = self.step3_user_interaction(cases, files)
        cases = res[0]
        files = res[1]
        requirements = res[2]

        self.step4_print_test_summary(cases, files, requirements, contexts)

        self.step5_write_and_print_tests(cases, files, contexts, requirements)

    def step1_find_symbol_context(self) -> Dict[str, List[Context]]:
        symbol_context = find_symbol_context_by_static_analysis(
            self.func_to_test, self.tui_lang.chat_language
        )

        known_context_for_llm: List[Context] = []
        if self.func_to_test.container_content is not None:
            known_context_for_llm.append(
                Context(
                    file_path=self.func_to_test.file_path,
                    content=self.func_to_test.container_content,
                    range=Range(
                        start=Position(line=self.func_to_test.container_start_line, character=0),
                        end=Position(line=self.func_to_test.container_end_line, character=0),
                    ),
                )
            )
        known_context_for_llm += list(
            {item for sublist in list(symbol_context.values()) for item in sublist}
        )

        recommended_context = find_symbol_context_of_llm_recommendation(
            self.func_to_test, known_context_for_llm
        )

        symbol_context.update(recommended_context)

        return symbol_context

    def step2_propose_cases_and_reference_files(
        self,
        contexts: List[Context],
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
                contexts=contexts,
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

    def step3_user_interaction(
        self,
        test_cases: List[str],
        reference_files: List[str],
    ) -> Tuple[List[str], List[str], str]:
        """
        Edit test cases and reference files by user.

        Return:
        - the updated cases
        - valid reference files
        - customized requirements(prompts)
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

        cached_requirements = self.local_cache.get("user_requirements") or ""
        requirements_editor = TextEditor(
            text=cached_requirements,
            title=_i(
                "Write your customized requirements(prompts) for tests here."
                "\n(For example, what testing framework to use.)"
            ),
        )

        form = Form(components=[checkbox, case_editor, ref_editor, requirements_editor])
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

        # Get customized requirements
        requirements: str = (
            requirements_editor.new_text.strip() if requirements_editor.new_text else ""
        )
        self.local_cache.set("user_requirements", requirements)

        return cases, valid_files, requirements

    # Tuple[List[str], List[str], str]:
    def step4_print_test_summary(
        self,
        cases: List[str],
        valid_files: List[str],
        requirements: str,
        contexts: List[Context],
    ):
        """
        Print the summary message in Step
        """
        _i = get_translation(self.tui_lang)

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
            # lines.append(_i("\nValid reference files:"))
            width = len(str(len(valid_files)))
            lines.extend([f"{(i+1):>{width}}. {f}" for i, f in enumerate(valid_files)])

        # if invalid_files:
        #     lines.append(_i("\nInvalid files:"))
        #     width = len(str(len(invalid_files)))
        #     lines.extend([f"{(i+1):>{width}}. {f}" for i, f in enumerate(invalid_files)])

        lines.append(_i("\nCustomized requirements(prompts):"))
        if requirements.strip():
            lines.append(requirements)
        else:
            lines.append(_i("No customized requirements."))

        if contexts:
            lines.append(_i("\nAdditional context:"))
            width = len(str(len(contexts)))
            lines.extend(
                [
                    f"{(i+1):>{width}}. {c.file_path}:{c.range.start.line+1}-{c.range.end.line+1}"
                    for i, c in enumerate(contexts)
                ]
            )

        with Step(title):
            print("\n".join(lines), flush=True)

    def step5_write_and_print_tests(
        self,
        cases: List[str],
        ref_files: List[str],
        symbol_contexts: List[Context],
        user_requirements: str,
    ):
        """
        Write and print tests.
        """

        write_and_print_tests(
            root_path=self.repo_root,
            func_to_test=self.func_to_test,
            test_cases=cases,
            reference_files=ref_files,
            symbol_contexts=symbol_contexts,
            user_requirements=user_requirements,
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
    ide_lang = IDEService().ide_language()
    local_cache = LocalCache("unit_tests", os.path.join(repo_root, *CHAT_WORKFLOW_DIR_PATH))

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
        workflow = UnitTestsWorkflow(
            user_prompt,
            func_to_test,
            repo_root,
            tui_lang,
            local_cache,
        )
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
