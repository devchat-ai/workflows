import os

USE_USER_MODEL = bool(os.environ.get("DEVCHAT_UNIT_TESTS_USE_USER_MODEL", False))
USER_LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4-turbo-preview")

DEFAULT_CONTEXT_SIZE = 4000
CONTEXT_SIZE = {
    "gpt-4-turbo-preview": 128000,
    "gpt-3.5-turbo": 16385,
    "gpt-4": 8192,
    "togetherai/mistralai/Mixtral-8x7B-Instruct-v0.1": 4000,
}

DEFAULT_ENCODING = "cl100k_base"
