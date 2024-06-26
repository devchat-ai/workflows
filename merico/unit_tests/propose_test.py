import json
from functools import partial
from typing import List, Optional

from devchat.llm.openai import chat_completion_no_stream_return_json
from find_context import Context
from llm_conf import (
    CONTEXT_SIZE,
    DEFAULT_CONTEXT_SIZE,
    DEFAULT_ENCODING,
    USE_USER_MODEL,
    USER_LLM_MODEL,
)
from model import FuncToTest, TokenBudgetExceededException
from openai_util import create_chat_completion_content
from prompts import PROPOSE_TEST_PROMPT
from tools.tiktoken_util import get_encoding
from tools.time_util import print_exec_time

MODEL = USER_LLM_MODEL if USE_USER_MODEL else "gpt-4-turbo-preview"  # "gpt-3.5-turbo"
ENCODING = (
    get_encoding(DEFAULT_ENCODING)  # Use default encoding as an approximation
    if USE_USER_MODEL
    else get_encoding("cl100k_base")
)
TOKEN_BUDGET = int(CONTEXT_SIZE.get(MODEL, DEFAULT_CONTEXT_SIZE) * 0.95)


def _mk_user_msg(
    user_prompt: str,
    func_to_test: FuncToTest,
    contexts: List[Context],
    chat_language: str,
) -> str:
    """
    Create a user message to be sent to the model within the token budget.
    """

    func_content = f"function code\n```\n{func_to_test.func_content}\n```\n"
    class_content = ""
    if func_to_test.container_content is not None:
        class_content = f"class code\n```\n{func_to_test.container_content}\n```\n"

    context_content = ""
    if contexts:
        context_content = "\n\nrelevant context\n\n"
        context_content += "\n\n".join([str(c) for c in contexts])
        context_content += "\n\n"

    # Prepare a list of user messages to fit the token budget
    # by adjusting the relevant content
    relevant_content_fmt = partial(
        PROPOSE_TEST_PROMPT.format,
        user_prompt=user_prompt,
        function_name=func_to_test.func_name,
        file_path=func_to_test.file_path,
        chat_language=chat_language,
    )
    # 0. func content & class content & context content
    msg_0 = relevant_content_fmt(
        relevant_content="\n".join([func_content, class_content, context_content]),
    )
    # 1. func content & class content
    msg_1 = relevant_content_fmt(
        relevant_content="\n".join([func_content, class_content]),
    )
    # 2. func content only
    msg_2 = relevant_content_fmt(
        relevant_content=func_content,
    )

    prioritized_msgs = [msg_0, msg_1, msg_2]

    for msg in prioritized_msgs:
        token_count = len(ENCODING.encode(msg, disallowed_special=()))
        if token_count <= TOKEN_BUDGET:
            return msg

    # Even func content exceeds the token budget
    raise TokenBudgetExceededException(
        f"Token budget exceeded while proposing test cases for <{func_to_test}>. "
        f"({token_count}/{TOKEN_BUDGET})"
    )


@print_exec_time("Model response time")
def propose_test(
    user_prompt: str,
    func_to_test: FuncToTest,
    contexts: Optional[List[Context]] = None,
    chat_language: str = "English",
) -> List[str]:
    """Propose test cases for a specified function based on a user prompt

    Args:
        user_prompt (str): The prompt or description for which test cases need to be generated.
        function_name (str): The name of the function to generate test cases for.
        file_path (str): The absolute path to the file containing the target function for which
                         test cases will be generated.

    Returns:
        List[str]: A list of test case descriptions.
    """
    contexts = contexts or []
    user_msg = _mk_user_msg(
        user_prompt=user_prompt,
        func_to_test=func_to_test,
        contexts=contexts,
        chat_language=chat_language,
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
        if not json_res:
            raise ValueError("No valid json response")

    else:
        # Use the openai api parameters
        content = create_chat_completion_content(
            model=MODEL,
            messages=[{"role": "user", "content": user_msg}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        json_res = json.loads(content)

    cases = json_res.get("test_cases", [])

    descriptions = []
    for case in cases:
        description = case.get("description", None)
        category = case.get("category", None)
        if description:
            if category:
                descriptions.append(category + ": " + description)
            else:
                descriptions.append(description)

    return descriptions
