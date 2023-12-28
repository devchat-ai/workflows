from typing import List, Optional

import tiktoken

from chat.ask_codebase.tools.retrieve_file_content import retrieve_file_content
from openai_util import create_chat_completion_chunks
from prompts import WRITE_TESTS_PROMPT
from model import FuncToTest, TokenBudgetExceededException


MODEL = "gpt-4-1106-preview"
TOKEN_BUDGET = int(128000 * 0.9)


def _mk_write_tests_msg(
    root_path: str,
    func_to_test: FuncToTest,
    test_cases: List[str],
    chat_language: str,
    reference_files: Optional[List[str]] = None,
) -> Optional[str]:
    encoding: tiktoken.Encoding = tiktoken.encoding_for_model(MODEL)

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

    func_content = f"function code\n```\n{func_to_test.func_content}\n```\n"
    class_content = ""
    if func_to_test.container_content is not None:
        class_content = f"class code\n```\n{func_to_test.container_content}\n```\n"

    # Adjust relevant content to fit the token budget

    # 1. both func content and class content
    relevant_content = "\n".join([func_content, class_content])

    user_msg = WRITE_TESTS_PROMPT.format(
        function_name=func_to_test.func_name,
        file_path=func_to_test.file_path,
        relevant_content=relevant_content,
        test_cases_str=test_cases_str,
        chat_language=chat_language,
        reference_tests_str=reference_tests_str,
    )
    tokens = len(encoding.encode(user_msg))
    if tokens <= TOKEN_BUDGET:
        return user_msg

    # 2. only func content
    relevant_content = func_content
    user_msg = WRITE_TESTS_PROMPT.format(
        function_name=func_to_test.func_name,
        file_path=func_to_test.file_path,
        relevant_content=relevant_content,
        test_cases_str=test_cases_str,
        chat_language=chat_language,
        reference_tests_str=reference_tests_str,
    )
    tokens = len(encoding.encode(user_msg))
    if tokens <= TOKEN_BUDGET:
        return user_msg

    # 3. even func content exceeds the token budget
    raise TokenBudgetExceededException(
        f"Token budget exceeded while writing test cases for <{func_to_test}>. "
        f"({tokens}/{TOKEN_BUDGET})"
    )


def write_and_print_tests(
    root_path: str,
    func_to_test: FuncToTest,
    test_cases: List[str],
    reference_files: Optional[List[str]] = None,
    chat_language: str = "English",
) -> None:
    user_msg = _mk_write_tests_msg(
        root_path=root_path,
        func_to_test=func_to_test,
        test_cases=test_cases,
        reference_files=reference_files,
        chat_language=chat_language,
    )

    chunks = create_chat_completion_chunks(
        model=MODEL,
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.1,
    )

    for chunk in chunks:
        if chunk.choices[0].finish_reason == "stop":
            break
        print(chunk.choices[0].delta.content, flush=True, end="")
