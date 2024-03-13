import json
from typing import List, Tuple

from devchat.llm.openai import chat_completion_no_stream_return_json
from llm_conf import (
    USE_USER_MODEL,
    USER_LLM_MODEL,
)
from openai_util import create_chat_completion_content

MODEL = USER_LLM_MODEL if USE_USER_MODEL else "gpt-3.5-turbo"

# ruff: noqa: E501

rerank_file_prompt = """
You're an advanced coding assistant. A user will present a coding question, and you'll be provided with a list of code files.
Based on the accumulated knowledge from previous analysis, respond with the files you should consult to answer the question, ordered by their relevance.
Assign a relevance score from 1 to 10 to each file, indicating how relevant you believe it is to the question.
Exclude any files that you deem irrelevant.
Only include file paths that are presented in the file path list.

Answer in JSON format:
{{
    "result": [
        {{"item": "<most relevant file path>", "relevance": 7}},
        {{"item": "<2nd most relevant file path>", "relevance": 4}},
        {{"item": "<3rd most relevant file path>", "relevance": 3}}
    ]
}}

Let's try this now:
{files}
Question: {question}
Accumulated Knowledge: {accumulated_knowledge}
Answer:
"""


def rerank_files(
    question: str,
    knowledge: str,
    items: List[str],
) -> List[Tuple[str, int]]:
    """
    Rerank a list of items based on the accumulated knowledge from previous analysis.
    """

    if not items:
        return []

    user_msg = ""

    files_str = ""
    for file in items:
        assert isinstance(file, str), "items must be a list of str when item_type is 'file'"
        files_str += f"- {file}\n"

    user_msg = rerank_file_prompt.format(
        files=files_str,
        question=question,
        accumulated_knowledge=knowledge,
    )

    result = {}
    if USE_USER_MODEL:
        # Use the wrapped api parameters
        result = (
            chat_completion_no_stream_return_json(
                messages=[
                    {
                        "role": "user",
                        "content": user_msg,
                    },
                ],
                llm_config={
                    "model": MODEL,
                    "temperature": 0.1,
                },
            )
            or {}
        )

    else:
        # Use the openai api parameters
        response = create_chat_completion_content(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": user_msg,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        result = json.loads(response)

    reranked = [(i["item"], i["relevance"]) for i in result.get("result", [])]

    return reranked
