from typing import Optional
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk

# TODO: make this file a common module


def create_chat_completion_chunks(
    client: Optional[OpenAI] = None, **kwargs
) -> Stream[ChatCompletionChunk]:
    """
    Create streaming responses.
    """
    _client = client or OpenAI()

    # Force to use streaming
    kwargs["stream"] = True

    return _client.chat.completions.create(**kwargs)


# TODO: handle connection errors and retry
def create_chat_completion_content(client: Optional[OpenAI] = None, **kwargs) -> str:
    """
    Request the completion in streaming mode to avoid long wait time.
    Then combine the chunks into a single string and return.

    This is a replacement of creating non-streaming chat completion.
    """
    _client = client or OpenAI()

    # Force to use streaming
    kwargs["stream"] = True

    results = []
    chunks = create_chat_completion_chunks(client=_client, **kwargs)
    for chunk in chunks:
        if chunk.choices[0].finish_reason == "stop":
            break
        print(len(results), flush=True)
        results.append(chunk.choices[0].delta.content)

    return "".join(results)
