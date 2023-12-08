import sys
import json

import openai

def chat_completion_no_stream(messages, llm_config, error_out: bool=True) -> str:
    connection_error = ''
    for _1 in range(3):
        try:
            response = openai.ChatCompletion.create(
                messages=messages,
                **llm_config,
                stream=False
            )
            
            response_dict = json.loads(str(response))
            if 'choices' not in response_dict:
                if error_out:
                    print("Response Error:", response_dict, file=sys.stderr, flush=True)
                return None
            respose_message = response_dict["choices"][0]["message"]
            # print("=> llm response:", respose_message, end="\n\n")
            return respose_message
        except ConnectionError as err:
            connection_error = err
            continue
        except Exception as err:
            if error_out:
                print("Exception:", err, file=sys.stderr, flush=True)
            return None
    if error_out:
        print("Connect Error:", connection_error, file=sys.stderr, flush=True)
    return None

def chat_completion_no_stream_return_json(messages, llm_config, error_out: bool=True):
    for _1 in range(3):
        response = chat_completion_no_stream(messages, llm_config)
        if response is None:
            return None

        try:
            response_obj = json.loads(response["content"])
            return response_obj
        except Exception:
            continue
    if error_out:
        print("Not valid json response:", response["content"], file=sys.stderr, flush=True)
    return None
