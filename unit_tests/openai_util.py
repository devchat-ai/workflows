import os
from typing import Optional

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk
from tenacity import retry, stop_after_attempt, wait_random_exponential

# TODO: make this file a common module


def create_chat_completion_chunks(
    client: Optional[OpenAI] = None, **kwargs
) -> Stream[ChatCompletionChunk]:
    """
    Create streaming responses.
    """
    _client = client or OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", None),
        base_url=os.environ.get("OPENAI_API_BASE", None),
    )

    # Force to use streaming
    kwargs["stream"] = True

    return _client.chat.completions.create(**kwargs)


RetryAttempts = 3


@retry(
    stop=stop_after_attempt(RetryAttempts),
    wait=wait_random_exponential(),
    reraise=True,
)
def create_chat_completion_content(client: Optional[OpenAI] = None, **kwargs) -> str:
    """
    Request the completion in streaming mode to avoid long wait time.
    Then combine the chunks into a single string and return.

    This is a replacement of creating non-streaming chat completion.
    """
    _client = client or OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", None),
        base_url=os.environ.get("OPENAI_API_BASE", None),
    )

    # Force to use streaming
    kwargs["stream"] = True

    results = []
    chunks = create_chat_completion_chunks(client=_client, **kwargs)
    for chunk in chunks:
        if chunk.choices[0].finish_reason == "stop":
            break
        results.append(chunk.choices[0].delta.content)

    return "".join(results)
