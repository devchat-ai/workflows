import os

USE_USER_MODEL = bool(os.environ.get("DEVCHAT_UNIT_TESTS_USE_USER_MODEL", False))
USER_LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4-turbo-preview")

DEFAULT_CONTEXT_SIZE = 4000
CONTEXT_SIZE = {
    "gpt-3.5-turbo": 16000,
    "gpt-4": 8000,
    "gpt-4-turbo-preview": 128000,
    "claude-3-sonnet": 1000000,
    "claude-3-opus": 1000000,
    "xinghuo-3.5": 8000,
    "GLM-4": 8000,
    "ERNIE-Bot-4.0": 8000,
    "togetherai/codellama/CodeLlama-70b-Instruct-hf": 4000,
    "togetherai/mistralai/Mixtral-8x7B-Instruct-v0.1": 16000,
    "minimax/abab6-chat": 8000,
    "llama-2-70b-chat": 4000,
}

DEFAULT_ENCODING = "cl100k_base"
