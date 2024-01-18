import json
import os
import sys
from typing import List, Tuple

from minimax_util import chat_completion_no_stream_return_json
from openai_util import create_chat_completion_content

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

rerank_file_prompt_cn = """
你是一位智能编程助手。
用户将给你一个文件列表并提出一个和编程相关的问题，
根据你对问题和每个文件可能包含的内容的理解，
找到文件列表中有助于回答该问题的文件，
并判断文件与问题的相关程度，从1到10为文件评分（10分表示相关度非常高，1分表示相关度很低），
最后将文件按相关度从高到低排序。

请注意，返回的所有文件路径都应在用户给出的文件列表里，不能额外添加文件，也不能修改文件路径。


以下是用户给出的文件列表：

{files}


用户的问题是: {question}
目前积累的相关背景知识: {accumulated_knowledge} 

请按以下JSON格式回复：
{{
    "result": [
        {{"item": "<最相关的文件路径>", "relevance": 7}},
        {{"item": "<第二相关的文件路径>", "relevance": 4}},
        {{"item": "<第三相关的文件路径>", "relevance": 3}}
    ]
}}


"""

RERANK_MODEL = "gpt-3.5-turbo-1106"


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

    user_msg = rerank_file_prompt_cn.format(
        files=files_str,
        question=question,
        accumulated_knowledge=knowledge,
    )

    model = os.environ.get("LLM_MODEL", RERANK_MODEL)
    result = chat_completion_no_stream_return_json(
        messages=[
            {
                "role": "user",
                "content": user_msg,
            },
        ],
        llm_config={
            "model": model,
            "temperature": 0.1,
        },
    )
    if not result:
        return []

    reranked = [(i["item"], i["relevance"]) for i in result["result"]]

    return reranked
