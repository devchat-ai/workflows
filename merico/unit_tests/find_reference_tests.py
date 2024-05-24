import json
from pathlib import Path
from typing import List

from devchat.llm.openai import chat_completion_no_stream_return_json
from llm_conf import (
    CONTEXT_SIZE,
    DEFAULT_CONTEXT_SIZE,
    DEFAULT_ENCODING,
    USE_USER_MODEL,
    USER_LLM_MODEL,
)
from openai_util import create_chat_completion_content
from tools.file_util import (
    is_not_hidden,
    is_source_code,
    is_test_file,
    verify_file_list,
)
from tools.git_util import git_file_of_interest_filter
from tools.tiktoken_util import get_encoding
from tools.time_util import print_exec_time

MODEL = USER_LLM_MODEL if USE_USER_MODEL else "gpt-4-turbo-preview"  # "gpt-3.5-turbo"
ENCODING = (
    get_encoding(DEFAULT_ENCODING)  # Use default encoding as an approximation
    if USE_USER_MODEL
    else get_encoding("cl100k_base")
)
TOKEN_BUDGET = int(CONTEXT_SIZE.get(MODEL, DEFAULT_CONTEXT_SIZE) * 0.95)


FIND_REF_TEST_PROMPT = """
As an advanced AI coding assistant,
you're given the task to identify suitable reference test files that can be used as a guide
for writing test cases for a specific function in the codebase.

You're provided with a list of test files in the repository.
Infer the purpose of each test file and identify the top 3 key files
that may be relevant to the target function and can serve as a reference for writing test cases.
The reference could provide a clear example of best practices
in testing functions of a similar nature.

The target function is {function_name}, located in the file {file_path}.
The list of test files in the repository is as follows:

{test_files_str}


Answer in JSON format with a list of the top 3 key file paths under the key `files`.
Make sure each file path is from the list of test files provided above.

Example:
{{
    "files": ["<file path 1>", "<file path 2>", "<file path 3>"]
}}

"""


def get_test_files(repo_root: str) -> List[str]:
    """
    Get all test files in the repository.
    """
    root = Path(repo_root)
    is_git_interest = git_file_of_interest_filter(repo_root)

    files = []
    for filepath in root.rglob("*"):
        relpath = filepath.relative_to(root)

        is_candidate = (
            filepath.is_file()
            and is_not_hidden(relpath)
            and is_git_interest(relpath)
            and is_source_code(str(filepath), only_code=True)
            and is_test_file(str(relpath))
        )

        if not is_candidate:
            continue

        files.append(str(relpath))

    return files


def _mk_user_msg(function_name: str, file_path: str, test_files: List[str]) -> str:
    """
    Create a user message to be sent to the model within the token budget.
    """
    test_files_str = "\n".join([f"- {f}" for f in test_files])
    msg = FIND_REF_TEST_PROMPT.format(
        function_name=function_name,
        file_path=file_path,
        test_files_str=test_files_str,
    )

    # TODO: check if the message fits within the token budget
    # and adjust the content accordingly
    return msg


@print_exec_time("Model response time")
def find_reference_tests(repo_root: str, function_name: str, file_path: str) -> List[str]:
    """Find reference tests for a specified function

    Args:
        repo_root (str): The path to the root directory of the codebase.
        function_name (str): The name of the function to generate test cases for.
        file_path (str): The path to the file containing the target function
                        for which test cases will be generated.

    Returns:
        List[str]: A list of paths to files that may contain a reference test
                    for the specified function.
    """
    test_files = get_test_files(repo_root)

    user_msg = _mk_user_msg(
        function_name=function_name,
        file_path=file_path,
        test_files=test_files,
    )

    json_res = {}
    if USE_USER_MODEL:
        # Use the wrapped api parameters
        json_res = (
            chat_completion_no_stream_return_json(
                messages=[{"role": "user", "content": user_msg}],
                llm_config={
                    "model": MODEL,
                    "temperature": 0.1,
                },
            )
            or {}
        )

    else:
        # Use the openai api parameters
        content = create_chat_completion_content(
            model=MODEL,
            messages=[{"role": "user", "content": user_msg}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        json_res = json.loads(content)

    files = json_res.get("files", [])
    ref_files = verify_file_list(files, repo_root)

    return ref_files
