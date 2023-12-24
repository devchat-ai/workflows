from typing import List
import tiktoken
import json

from openai_util import create_chat_completion_content
from prompts import PROPOSE_TEST_PROMPT


MODEL = "gpt-3.5-turbo-1106"
# MODEL = "gpt-4-1106-preview"


def propose_test(
    repo_root: str,
    user_prompt: str,
    function_name: str,
    function_content: str,
    file_path: str,
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

    encoding: tiktoken.Encoding = tiktoken.encoding_for_model(MODEL)
    token_budget = 16000 * 0.9

    user_msg = PROPOSE_TEST_PROMPT.format(
        user_prompt=user_prompt,
        function_name=function_name,
        file_path=file_path,
        function_content=function_content,
        chat_language=chat_language,
    )

    tokens = len(encoding.encode(user_msg))
    if tokens > token_budget:
        return f"Token budget exceeded while generating test cases. ({tokens}/{token_budget})"

    content = create_chat_completion_content(
        model=MODEL,
        messages=[{"role": "user", "content": user_msg}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    cases = json.loads(content).get("test_cases", [])

    descriptions = []
    for case in cases:
        description = case.get("description", None)
        if description:
            descriptions.append(description)

    return descriptions
