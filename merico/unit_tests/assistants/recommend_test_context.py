import json
from typing import List, Optional

from devchat.llm.openai import chat_completion_no_stream_return_json
from llm_conf import (
    CONTEXT_SIZE,
    DEFAULT_CONTEXT_SIZE,
    DEFAULT_ENCODING,
    USE_USER_MODEL,
    USER_LLM_MODEL,
)
from model import FuncToTest
from openai_util import create_chat_completion_content
from tools.tiktoken_util import get_encoding
from tools.time_util import print_exec_time

MODEL = USER_LLM_MODEL if USE_USER_MODEL else "gpt-4-turbo-preview"
ENCODING = (
    get_encoding(DEFAULT_ENCODING)  # Use default encoding as an approximation
    if USE_USER_MODEL
    else get_encoding("cl100k_base")
)

TOKEN_BUDGET = int(CONTEXT_SIZE.get(MODEL, DEFAULT_CONTEXT_SIZE) * 0.9)


# ruff: noqa: E501
recommend_symbol_context_prompt = """
You're an advanced AI test generator.

You're about to write test cases for the function `{function_name}` in the file `{file_path}`.
Before you start, you need to check if you have enough context information to write the test cases.

Here is the source code of the function:

```
{function_content}
```

And here are some context information that might help you write the test cases:


{context_content}


Do you think the context information is enough?
If the information is insufficient, recommend which symbols or types you need to know more about.

Return a JSON object with a single key "key_symbols" whose value is a list of strings.
- If the context information is enough, return an empty list.
- Each string is the name of a symbol or type appearing in the function that lacks context information for writing test.
- The list should contain the most important symbols and should not exceed 10 items.

JSON Format Example:
{{
    "key_symbols": ["<symbol 1>", "<symbol 2>", "<symbol 3>",...]
}}

"""


def _mk_user_msg(func_to_test: FuncToTest, contexts: List) -> str:
    """
    Create a user message to be sent to the model within the token budget.
    """
    msg = None
    while msg is None:
        context_content = "\n\n".join([str(c) for c in contexts])

        msg = recommend_symbol_context_prompt.format(
            function_content=func_to_test.func_content,
            context_content=context_content,
            function_name=func_to_test.func_name,
            file_path=func_to_test.file_path,
        )

        token_count = len(ENCODING.encode(msg, disallowed_special=()))
        if contexts and token_count > TOKEN_BUDGET:
            # Remove the last context and try again
            contexts.pop()
            msg = None

    return msg


@print_exec_time("Model response time")
def get_recommended_symbols(
    func_to_test: FuncToTest, known_context: Optional[List] = None
) -> List[str]:
    known_context = known_context or []
    msg = _mk_user_msg(func_to_test, known_context)

    json_res = {}
    if USE_USER_MODEL:
        # Use the wrapped api parameters
        json_res = (
            chat_completion_no_stream_return_json(
                messages=[{"role": "user", "content": msg}],
                llm_config={
                    "model": MODEL,
                    "temperature": 0.1,
                },
            )
            or {}
        )

    else:
        response = create_chat_completion_content(
            model=MODEL,
            messages=[{"role": "user", "content": msg}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        json_res = json.loads(response)

    key_symbols = json_res.get("key_symbols", [])

    return key_symbols
