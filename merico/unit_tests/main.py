# ruff: noqa: E402
import os
import sys

import click
import openai

sys.path.append(os.path.dirname(__file__))

from i18n import TUILanguage, get_translation
from model import (
    FuncToTest,
    TokenBudgetExceededException,
    UserCancelledException,
)
from ut_workflow import UnitTestsWorkflow

from cache import LocalCache
from lib.chatmark import Step
from lib.ide_service import IDEService

CHAT_WORKFLOW_DIR_PATH = [".chat", "workflows"]


@click.command()
@click.argument("input", required=True)
def main(input: str):
    """
    The main entry point for the unit tests generation workflow.
    "/unit_tests {a}:::{b}:::{c}:::{d}:::{e}:::{f}"
    """
    # Parse input
    try:
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

        func_start_line = int(func_start_line)
        func_end_line = int(func_end_line)
        container_start_line = int(container_start_line)
        container_end_line = int(container_end_line)
    except Exception as e:
        readme = os.path.join(os.path.dirname(__file__), "README.md")
        if os.path.exists(readme):
            with open(readme, "r", encoding="utf-8") as f:
                readme_text = f.read()
                print(readme_text)
            return

        else:
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

    except (openai.APIConnectionError, openai.APITimeoutError) as e:
        msg = "Model API connection error. Please try again later."
        with Step(msg):
            print(f"\n{e}\n", flush=True)

    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
