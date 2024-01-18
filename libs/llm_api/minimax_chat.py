import json
import os
import sys
import time

import requests


class StreamIterWrapper:
    def __init__(self, response):
        self.response = response
        self.create_time = int(time.time())
        self.line_iterator = response.iter_lines()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            response_line = next(self.line_iterator)
            if response_line == b"":
                return self.__next__()
            if response_line == b"\n":
                return self.__next__()

            response_line = response_line.replace(b"data: ", b"")
            response_result = json.loads(response_line.decode("utf-8"))
            if response_result["choices"][0].get("finish_reason", "") == "stop":
                raise StopIteration

            stream_response = {
                "id": f"minimax_{self.create_time}",
                "created": self.create_time,
                "object": "chat.completion.chunk",
                "model": response_result["model"],
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "delta": {
                            "role": "assistant",
                            "content": response_result["choices"][0]["messages"][0]["text"],
                        },
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 100},
            }

            return stream_response
        except StopIteration as exc:  # If there is no more event
            raise StopIteration from exc
        except Exception as err:
            print("Exception:", err.__class__.__name__, err, file=sys.stderr, end="\n\n")
            raise StopIteration from err


def chat_completion(messages, llm_config):
    url = _make_api_url()
    headers = _make_header()
    if _is_private_llm():
        payload = _make_private_payload(messages, llm_config)
    else:
        payload = _make_public_payload(messages, llm_config)

    response = requests.post(url, headers=headers, json=payload)
    return response


def stream_chat_completion(messages, llm_config):
    url = _make_api_url()
    headers = _make_header()
    if _is_private_llm():
        payload = _make_private_payload(messages, llm_config, True)
    else:
        payload = _make_public_payload(messages, llm_config, True)

    response = requests.post(url, headers=headers, json=payload)
    streamIters = StreamIterWrapper(response)
    return streamIters


def _is_private_llm():
    api_base_url = os.environ.get("OPENAI_API_BASE", "")
    return not api_base_url.startswith("https://api.minimax.chat")


def _make_api_url():
    api_base_url = os.environ.get("OPENAI_API_BASE", None)
    if not api_base_url:
        raise ValueError("minimax api url is not set")

    if api_base_url.startswith("https://api.minimax.chat"):
        if api_base_url.endswith("/"):
            api_base_url = api_base_url[:-1]
        if not api_base_url.endswith("/v1"):
            api_base_url = api_base_url + "/v1"
        api_base_url += "/text/chatcompletion_pro"

        api_key = os.environ.get("OPENAI_API_KEY", None)
        if not api_key:
            raise ValueError("minimax api key is not set")

        group_id = api_key.split("##")[0]
        api_base_url += f"?GroupId={group_id}"
        return api_base_url
    else:
        if api_base_url.endswith("/"):
            api_base_url = api_base_url[:-1]
        if not api_base_url.endswith("/interact"):
            api_base_url = api_base_url + "/interact"
        return api_base_url


def _make_api_key():
    if _is_private_llm():
        return ""

    api_key = os.environ.get("OPENAI_API_KEY", None)
    return api_key.split("##")[1]


def _make_header():
    api_key = _make_api_key()
    return {
        **({"Authorization": f"Bearer {api_key}"} if not _is_private_llm() else {}),
        "Content-Type": "application/json",
    }


def _to_private_messages(messages):
    new_messages = []
    for message in messages:
        if message["role"] == "user":
            new_messages.append({"role": "user", "name": "user", "text": message["content"]})
        else:
            new_messages.append({"role": "ai", "name": "ai", "text": message["content"]})
    new_messages.append({"role": "ai", "name": "ai", "text": ""})
    return new_messages


def _make_private_payload(messages, llm_config, stream=False):
    return {
        "data": _to_private_messages(messages),
        "model_control": {
            "system_data": [
                {
                    "role": "system",
                    "ai_setting": "ai",
                    "text": "你是minimax编码助理，擅长编写代码，编写注释，编写测试用例，并且很注重编码的规范性。",
                },
            ],
            # "alpha_frequency": 128,
            # "alpha_frequency_src": 1,
            # "alpha_presence": 0,
            # "alpha_presence_src": 0,
            # "block_ngram": 0,
            # "clean_init_no_penalty_list": True,
            # "context_block_ngram": 0,
            # "factual_topp": False,
            # "lamda_decay": 1,
            # "length_penalty": 1,
            # "no_penalty_list": ",",
            # "omega_bound": 0,
            # "repeat_filter": False,
            # "repeat_sampling": 1,
            # "skip_text_mask": True,
            "tokens_to_generate": llm_config.get("max_tokens", 512),
            # "sampler_type": "nucleus",
            "beam_width": 1,
            # "delimiter": "\n",
            # "min_length": 0,
            # "skip_info_mask": True,
            "stop_sequence": [],
            # "top_p": 0.95,
            "temperature": llm_config.get("temperature", 0.95),
        },
        "stream": stream,
    }


def _to_public_messages(messages):
    new_messages = []
    for message in messages:
        if message["role"] == "user":
            new_messages.append(
                {"sender_type": "USER", "sender_name": "USER", "text": message["content"]}
            )
        else:
            new_messages.append(
                {"sender_type": "BOT", "sender_name": "ai", "text": message["content"]}
            )
    return new_messages


def _make_public_payload(messages, llm_config, stream=False):
    response = {
        "model": "abab5.5-chat",
        "tokens_to_generate": llm_config.get("max_tokens", 512),
        "temperature": llm_config.get("temperature", 0.1),
        # "top_p": 0.9,
        "reply_constraints": {"sender_type": "BOT", "sender_name": "ai"},
        "sample_messages": [],
        "plugins": [],
        "messages": _to_public_messages(messages),
        "bot_setting": [
            {
                "bot_name": "ai",
                "content": (
                    "MM智能助理是一款由MiniMax自研的，"
                    "没有调用其他产品的接口的大型语言模型。"
                    "MiniMax是一家中国科技公司，一直致力于进行大模型相关的研究。"
                ),
            }
        ],
        "stream": stream,
    }
    return response
