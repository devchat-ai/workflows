from typing import List, Optional

import tiktoken

from chat.ask_codebase.tools.retrieve_file_content import retrieve_file_content
from openai_util import create_chat_completion_chunks
from prompts import WRITE_TESTS_PROMPT


MODEL = "gpt-4-1106-preview"


def _mk_write_tests_msg(
    root_path: str,
    function_name: str,
    function_content: str,
    file_path: str,
    test_cases: List[str],
    chat_language: str,
    reference_files: Optional[List[str]] = None,
) -> Optional[str]:
    encoding: tiktoken.Encoding = tiktoken.encoding_for_model(MODEL)

    # cost saving
    token_budget = 16000 * 0.9

    test_cases_str = ""
    for i, test_case in enumerate(test_cases, 1):
        test_cases_str += f"{i}. {test_case}\n"

    if reference_files:
        reference_tests_str = ""
        for i, fp in enumerate(reference_files, 1):
            reference_test_content = retrieve_file_content(fp, root_path)
            reference_tests_str += f"{i}. {fp}\n\n"
            reference_tests_str += f"```{reference_test_content}```\n"
    else:
        reference_tests_str = "No reference test cases provided."

    user_msg = WRITE_TESTS_PROMPT.format(
        function_name=function_name,
        file_path=file_path,
        function_str=function_content,
        test_cases_str=test_cases_str,
        chat_language=chat_language,
        reference_tests_str=reference_tests_str,
    )

    tokens = len(encoding.encode(user_msg))
    if tokens > token_budget:
        # "Token budget exceeded while generating test cases."
        # TODO: how ot handle token budget exceeded
        return None

    return user_msg


def write_and_print_tests(
    root_path: str,
    function_name: str,
    function_content: str,
    file_path: str,
    test_cases: List[str],
    reference_files: Optional[List[str]] = None,
    chat_language: str = "English",
) -> None:
    user_msg = _mk_write_tests_msg(
        root_path=root_path,
        function_name=function_name,
        function_content=function_content,
        file_path=file_path,
        test_cases=test_cases,
        reference_files=reference_files,
        chat_language=chat_language,
    )
    if not user_msg:
        # TODO: how ot handle token budget exceeded
        print("Token budget exceeded while generating test cases.", flush=True)

    chunks = create_chat_completion_chunks(
        model=MODEL,
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.1,
    )

    for chunk in chunks:
        if chunk.choices[0].finish_reason == "stop":
            break
        print(chunk.choices[0].delta.content, flush=True, end="")
