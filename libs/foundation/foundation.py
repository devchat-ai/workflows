import json
import os


def get_devchat_site_packages_path():
    """@DevChatApi
    Retrieve the DevChat site packages path from the environment variable.

    Returns:
        str: The path stored in DEVCHAT_PYTHONPATH environment variable,
             or an empty string if the variable isn't set.
    """
    return os.environ.get("DEVCHAT_PYTHONPATH", "")


def get_llm_model():
    """@DevChatApi
    Retrieve the DevChat LLM model from the environment variable.

    Returns:
        str: The LLM model stored in LLM_MODEL environment variable,
             or an empty string if the variable isn't set.
    """
    return os.environ.get("LLM_MODEL", "gpt-3.5-turbo-1106")


def get_parent_hash():
    """@DevChatApi
    Retrieves the parent hash value from the environment variable.

    This function is designed to obtain the hash value of the parent message in a sequence of
    chat interactions,
    where each pair of question and response is associated with respective hash values.
    It helps in reconstructing
    the order of conversation threads by providing the parent hash for the current message.

    Returns:
        str: The parent hash value stored in the PARENT_HASH environment variable,
             or an empty string if the variable isn't set.
    """
    return os.environ.get("PARENT_HASH", "")


def get_context_contents():
    """@DevChatApi
    Retrieve the chat context history from an environment variable.

    This function looks up the `CONTEXT_CONTENTS` environment variable, parses it as JSON,
    and returns the result.
    It's used to obtain the historical content of the chat, which is stored in a JSON array format.
    Each item in the array represents a message with a sender role and content, for example:
    [{"role": "user", "content": "User's message"},
     {"role": "assistant", "content": "Assistant's reply"}].

    Returns:
        list: A list of dictionaries representing the chat history. Each dictionary
              contains the keys 'role' and
              'content', corresponding to who sent the message and what the message was,
              respectively. If the `CONTEXT_CONTENTS` variable is not set, an empty list
              is returned.
    """
    return json.loads(os.environ.get("CONTEXT_CONTENTS", "[]"))


def get_user_input_text():
    """@DevChatApi
    Fetch the most recent user input from the chat context.

    This function retrieves the current chat context by calling the
    `get_context_contents` function, which returns a list of message
    dictionaries. It then extracts the content of the last message in the
    context, assuming it's from the user, returning it as a string. If the
    context is empty, an empty string is returned. This function is typically
    used to get the last input provided by the user in the chat interface.

    Returns:
        str: The content of the most recent user input message if it exists,
             otherwise an empty string.
    """
    contexts = get_context_contents()
    user_index = 0
    for index, context in enumerate(contexts):
        if context["role"] == "user":
            user_index = index
    return contexts[user_index]["content"] if len(contexts) > 0 else ""


# 获取用户输入的相关文件内容。这些相关文件一般通过Add to DevChat右键菜单添加到聊天上下文中。
def get_user_input_files():
    """@DevChatApi
    Retrieve a list of file contents that were input by the user.

    This function scans through the chat context (which contains all messages and interactions
    within a chat session) to identify any files that were added by the user, typically via the
    'Add to DevChat' right-click context menu option. Files added by the user are delineated in the
    chat context as having a 'role' other than 'assistant'. This function finds the last occurrence
    of a message where the 'assistant' role is responsible and then returns the content of all
    subsequent messages until the penultimate one, assuming these are the user's input files.

    Returns:
        list[str]: A list of the content from all files that were input by the user. Each item
                   in the list is the contents of one file.
    """
    contexts = get_context_contents()
    last_index = 0
    for index, item in enumerate(contexts):
        if item["role"] == "user":
            last_index = index + 1
    if last_index == len(contexts):
        return []
    return [item["content"] for item in contexts[last_index:]]
