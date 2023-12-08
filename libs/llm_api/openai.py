import re
import sys
import json

import openai


def _try_remove_markdown_block_flag(content):
    """
    如果content是一个markdown块，则删除它的头部```xxx和尾部```
    """
    # 定义正则表达式模式，用于匹配markdown块的头部和尾部
    pattern = r"^\s*```\s*(\w+)\s*\n(.*?)\n\s*```\s*$"

    # 使用re模块进行匹配
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)

    if match:
        # 如果匹配成功，则提取出markdown块的内容并返回
        _ = match.group(1)  # language
        markdown_content = match.group(2)
        return markdown_content.strip()
    else:
        # 如果匹配失败，则返回原始内容
        return content


def chat_completion_no_stream(messages, llm_config, error_out: bool = True) -> str:
    """
    通过ChatCompletion API获取OpenAI聊天机器人的回复。

    Args:
        messages: 一个列表，包含用户输入的消息。
        llm_config: 一个字典，包含ChatCompletion API的配置信息。
        error_out: 如果为True，遇到异常时输出错误信息并返回None，否则返回None。

    Returns:
        如果成功获取到聊天机器人的回复，返回一个字符串类型的回复消息。如果连接失败，则返回None。

    """
    connection_error = ""
    for _1 in range(3):
        try:
            response = openai.ChatCompletion.create(messages=messages, **llm_config, stream=False)

            response_dict = json.loads(str(response))
            if "choices" not in response_dict:
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


def chat_completion_no_stream_return_json(messages, llm_config, error_out: bool = True):
    """
    尝试三次从聊天完成API获取结果，并返回JSON对象。
    如果无法解析JSON，将尝试三次，直到出现错误或达到最大尝试次数。

    Args:
        messages (List[str]): 用户输入的消息列表。
        llm_config (Dict[str, Any]): 聊天配置字典。
        error_out (bool, optional): 如果为True，则如果出现错误将打印错误消息并返回None。默认为True。

    Returns:
        Dict[str, Any]: 从聊天完成API获取的JSON对象。
            如果无法解析JSON或达到最大尝试次数，则返回None。
    """
    for _1 in range(3):
        response = chat_completion_no_stream(messages, llm_config)
        if response is None:
            return None

        try:
            # json will format as ```json ... ``` in 1106 model
            response_content = _try_remove_markdown_block_flag(response["content"])
            response_obj = json.loads(response_content)
            return response_obj
        except Exception:
            continue
    if error_out:
        print("Not valid json response:", response["content"], file=sys.stderr, flush=True)
    return None
