import json
from pathlib import Path
from typing import Callable, List

from assistants.directory_structure.base import DirectoryStructureBase
from assistants.rerank_files import rerank_files
from devchat.llm.openai import chat_completion_no_stream_return_json
from llm_conf import (
    CONTEXT_SIZE,
    DEFAULT_CONTEXT_SIZE,
    DEFAULT_ENCODING,
    USE_USER_MODEL,
    USER_LLM_MODEL,
)
from openai_util import create_chat_completion_content
from tools.directory_viewer import ListViewer
from tools.tiktoken_util import get_encoding
from tools.time_util import print_exec_time

MODEL = USER_LLM_MODEL if USE_USER_MODEL else "gpt-4-turbo-preview"  # "gpt-3.5-turbo"
ENCODING = (
    get_encoding(DEFAULT_ENCODING)  # Use default encoding as an approximation
    if USE_USER_MODEL
    else get_encoding("cl100k_base")
)
TOKEN_BUDGET = int(CONTEXT_SIZE.get(MODEL, DEFAULT_CONTEXT_SIZE) * 0.95)


class RelevantFileFinder(DirectoryStructureBase):
    def _paginate_dir_structure(
        self, criteria: Callable[[Path], bool], style: str = "list"
    ) -> List[str]:
        """
        Automatically paginate the dir structure to ensure
        each page is within the token budget.
        """
        # Currently only support list style
        viewer = ListViewer(root_path=self.root_path, criteria=criteria)
        item_count = len(viewer.items)

        pages = []
        page_num = 1
        while True:
            pages.clear()
            page_size = (item_count // page_num) + 1

            # Visualize the dir structure with pagination
            for i in range(page_num):
                pages.append(viewer.visualize(page_size=page_size, page=i))

            # Check if each page is within the token budget
            within_budget = True
            for p in pages:
                tokens = len(ENCODING.encode(p, disallowed_special=()))
                if tokens > TOKEN_BUDGET:
                    within_budget = False
                    break

            if within_budget:
                break

            # Divide dir structure into more pages
            page_num += 1

        return pages

    def _mk_message(self, objective: str, dir_structure: str) -> str:
        message = (
            "As an advanced AI, you're given the task to understand the structure "
            "of a codebase, infer the purpose of each directory, and identify the "
            "top 10 key files relevant to a specific objective or question."
            "\n"
            "Your goal is not to analyze the code within the files, but rather to "
            "analyze the structure of the project and determine which files might "
            "contain the necessary information or code to meet the user's needs."
            "\n\n"
            "Here's the directory structure of the project:"
            "\n\n"
            f"{dir_structure}"
            "\n\n"
            "Based on your understanding, help me find the top 10 key files "
            "relevant to the following objective or question:"
            "\n"
            f'"{objective}"'
            "\n"
            "\n"
            "Output should be a JSON object with a list of the top 10 file paths "
            "under the key `files`."
        )

        return message

    @print_exec_time("Model response time")
    def _find_relevant_files(self, objective: str, dir_structure_pages: List[str]) -> List[str]:
        files: List[str] = []
        for dir_structure in dir_structure_pages:
            user_msg = self._mk_message(objective, dir_structure)

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

            else:
                # Use the openai api parameters
                response = create_chat_completion_content(
                    model=MODEL,
                    messages=[
                        {"role": "user", "content": user_msg},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
                json_res = json.loads(response)

            files.extend(json_res.get("files", []))

        reranked = rerank_files(
            question=objective,
            knowledge="",
            items=files,
        )

        return [i[0] for i in reranked]

    def analyze(self, objective: str) -> List[str]:
        """
        Find the key files relevant to a specific objective or question.
        """
        criteria = self.mk_repo_criteria()

        dir_pages = self._paginate_dir_structure(criteria=criteria)

        return self._find_relevant_files(objective, dir_pages)
