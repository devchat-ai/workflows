from functools import partial
from typing import List, Optional

from devchat.llm.chat import chat_completion_stream_out
from find_context import Context
from llm_conf import (
    CONTEXT_SIZE,
    DEFAULT_CONTEXT_SIZE,
    DEFAULT_ENCODING,
    USE_USER_MODEL,
    USER_LLM_MODEL,
)
from model import FuncToTest, TokenBudgetExceededException
from openai_util import create_chat_completion_chunks
from prompts import WRITE_TESTS_PROMPT
from tools.file_util import retrieve_file_content
from tools.tiktoken_util import get_encoding

MODEL = USER_LLM_MODEL if USE_USER_MODEL else "gpt-4-turbo-preview"
ENCODING = (
    get_encoding(DEFAULT_ENCODING)  # Use default encoding as an approximation
    if USE_USER_MODEL
    else get_encoding("cl100k_base")
)
TOKEN_BUDGET = int(CONTEXT_SIZE.get(MODEL, DEFAULT_CONTEXT_SIZE) * 0.9)


def _mk_write_tests_msg(
    root_path: str,
    func_to_test: FuncToTest,
    test_cases: List[str],
    chat_language: str,
    reference_files: Optional[List[str]] = None,
    # context_files: Optional[List[str]] = None,
    symbol_contexts: Optional[List[Context]] = None,
    user_requirements: str = "",
) -> Optional[str]:
    additional_requirements = ""
    if user_requirements:
        additional_requirements = f"Additional requirements\n\n{user_requirements}\n\n"

    test_cases_str = ""
    for i, test_case in enumerate(test_cases, 1):
        test_cases_str += f"{i}. {test_case}\n"

    reference_content = "\nContent of reference test code:\n\n"
    if reference_files:
        for i, fp in enumerate(reference_files, 1):
            reference_test_content = retrieve_file_content(fp, root_path)
            reference_content += f"{i}. {fp}\n\n"
            reference_content += f"```{reference_test_content}```\n\n"
    else:
        reference_content += "No reference test cases provided.\n\n"

    func_content = f"\nfunction code\n```\n{func_to_test.func_content}\n```\n"
    class_content = ""
    if func_to_test.container_content is not None:
        class_content = f"\nclass code\n```\n{func_to_test.container_content}\n```\n"

    context_content = ""
    if symbol_contexts:
        context_content += "\n\nrelevant context\n\n"
        context_content += "\n\n".join([str(c) for c in symbol_contexts])
        context_content += "\n\n"

    # if context_files:
    #     context_content += "\n\nrelevant context files\n\n"
    #     for i, fp in enumerate(context_files, 1):
    #         context_file_content = retrieve_file_content(fp, root_path)
    #         context_content += f"{i}. {fp}\n\n"
    #         context_content += f"```{context_file_content}```\n\n"

    # Prepare a list of user messages to fit the token budget
    # by adjusting the relevant content and reference content
    content_fmt = partial(
        WRITE_TESTS_PROMPT.format,
        function_name=func_to_test.func_name,
        file_path=func_to_test.file_path,
        test_cases_str=test_cases_str,
        chat_language=chat_language,
        additional_requirements=additional_requirements,
    )

    # NOTE: adjust symbol_context content more flexibly if needed
    msg_0 = content_fmt(
        relevant_content="\n".join([func_content, class_content, context_content]),
        reference_content=reference_content,
    )

    # 1. func content & class content & reference file content
    msg_1 = content_fmt(
        relevant_content="\n".join([func_content, class_content]),
        reference_content=reference_content,
    )
    # 2. func content & class content
    msg_2 = content_fmt(
        relevant_content="\n".join([func_content, class_content]),
        reference_content="",
    )
    # 3. func content only
    msg_3 = content_fmt(
        relevant_content=func_content,
        reference_content="",
    )

    prioritized_msgs = [msg_0, msg_1, msg_2, msg_3]

    for msg in prioritized_msgs:
        tokens = len(ENCODING.encode(msg, disallowed_special=()))
        if tokens <= TOKEN_BUDGET:
            return msg

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
    symbol_contexts: Optional[List[Context]] = None,
    user_requirements: str = "",
    chat_language: str = "English",
) -> None:
    user_msg = _mk_write_tests_msg(
        root_path=root_path,
        func_to_test=func_to_test,
        test_cases=test_cases,
        reference_files=reference_files,
        symbol_contexts=symbol_contexts,
        user_requirements=user_requirements,
        chat_language=chat_language,
    )

    if USE_USER_MODEL:
        # Use the wrapped api
        _ = chat_completion_stream_out(
            messages=[{"role": "user", "content": user_msg}],
            llm_config={"model": MODEL, "temperature": 0.1},
        )

    else:
        # Use the openai api parameters
        chunks = create_chat_completion_chunks(
            model=MODEL,
            messages=[{"role": "user", "content": user_msg}],
            temperature=0.1,
        )
        for chunk in chunks:
            if chunk.choices[0].finish_reason == "stop":
                break

            content = chunk.choices[0].delta.content
            if content is not None:
                print(content, flush=True, end="")
