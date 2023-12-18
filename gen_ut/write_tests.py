import os
from pathlib import Path
from typing import List, Optional

import tiktoken

from chat.ask_codebase.tools.retrieve_file_content import retrieve_file_content
from chat.util.openai_util import create_chat_completion


MODEL = "gpt-4-1106-preview"
WRITE_TESTS_PROMPT = """
You're an advanced AI test case generator.
Given a target function, some reference test code, and a list of specific test case descriptions, write the test cases in code.
Each test case should be self-contained and executable.
Use the content of the reference test cases as a model, ensuring you use the same test framework and mock library,
and apply comparable mocking strategies and best practices.


The target function is {function_name}, located in the file {file_path}.
Here's the source code of the function:
```
{function_str}
```
Content of reference test code:

{reference_tests_str}

Here's the list of test case descriptions:

{test_cases_str}

Answer in the following format:

Test Case 1. <original test case 1 description>

<test case 1 code>

Test Case 2. <original test case 2 description>

<test case 2 code>
"""


def write_tests(
    root_path: str,
    function_name: str,
    function_content: str,
    file_path: str,
    test_cases: List[str],
    reference_files: Optional[List[str]] = None,
) -> str:
    encoding: tiktoken.Encoding = tiktoken.encoding_for_model(MODEL)

    # cost saving
    token_budget = 16000 * 0.9

    test_cases_str = ""
    for i, test_case in enumerate(test_cases, 1):
        test_cases_str += f"{i}. {test_case}\n"

    if reference_files:
        reference_tests_str = ""
        for i, fp in enumerate(reference_files, 1):
            reference_test_content = retrieve_file_content(
                str(Path(root_path) / fp), root_path
            )
            reference_tests_str += f"{i}. {fp}\n\n"
            reference_tests_str += f"```{reference_test_content}```\n"
    else:
        reference_tests_str = "No reference test cases provided."

    user_msg = WRITE_TESTS_PROMPT.format(
        function_name=function_name,
        file_path=file_path,
        function_str=function_content,
        test_cases_str=test_cases_str,
        reference_tests_str=reference_tests_str,
    )

    tokens = len(encoding.encode(user_msg))
    if tokens > token_budget:
        return "Token budget exceeded while generating test cases."

    response = create_chat_completion(
        model=MODEL,
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.1,
    )

    content = response.choices[0].message.content

    return content
