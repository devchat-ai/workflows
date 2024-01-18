import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))

from llm_api import (
    chat_completion_no_stream_return_json,
    chat_completion_stream,
)
