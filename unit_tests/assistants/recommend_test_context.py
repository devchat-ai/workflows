import json
from typing import List, Optional

from model import FuncToTest
from openai_util import create_chat_completion_content

MODEL = "gpt-4-1106-preview"
ENCODING = "cl100k_base"
# TODO: handle token budget
TOKEN_BUDGET = int(128000 * 0.9)


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


def get_recommended_symbols(
    func_to_test: FuncToTest, known_context: Optional[List] = None
) -> List[str]:
    known_context = known_context or []
    context_content = "\n\n".join([str(c) for c in known_context])

    msg = recommend_symbol_context_prompt.format(
        function_content=func_to_test.func_content,
        context_content=context_content,
        function_name=func_to_test.func_name,
        file_path=func_to_test.file_path,
    )

    response = create_chat_completion_content(
        model=MODEL,
        messages=[{"role": "user", "content": msg}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    key_symbols = json.loads(response).get("key_symbols", [])

    return key_symbols
