"""
/pr.describe https://github.com/devchat-ai/devchat-vscode/pull/25
"""
# ruff: noqa: E402

import logging
import os
import sys

# add the current directory to the path
# add new model configs to algo.MAX_TOKENS
import pr_agent.algo as algo

from lib.ide_service import IDEService
from merico.pr.config_util import get_model_max_input

algo.MAX_TOKENS["gpt-4-turbo-preview"] = 128000
algo.MAX_TOKENS["claude-3-opus"] = 100000
algo.MAX_TOKENS["claude-3-sonnet"] = 100000
algo.MAX_TOKENS["claude-3-haiku"] = 100000
algo.MAX_TOKENS["ERNIE-Bot-4.0"] = 8000
algo.MAX_TOKENS["GLM-4"] = 8000
algo.MAX_TOKENS["hzwxai/Mixtral-8x7B-Instruct-v0.1-GPTQ"] = 16000
algo.MAX_TOKENS["minimax/abab6-chat"] = 8000
algo.MAX_TOKENS["xinghuo-3.5"] = 8000
algo.MAX_TOKENS["llama-2-70b-chat"] = 4000
algo.MAX_TOKENS["togetherai/codellama/CodeLlama-70b-Instruct-hf"] = 4000
algo.MAX_TOKENS["togetherai/mistralai/Mixtral-8x7B-Instruct-v0.1"] = 16000
algo.MAX_TOKENS["text-embedding-ada-002"] = 8000
algo.MAX_TOKENS["text-embedding-3-small"] = 8000
algo.MAX_TOKENS["text-embedding-3-large"] = 8000
algo.MAX_TOKENS["embedding-v1"] = 8000
algo.MAX_TOKENS["embedding-2"] = 8000
algo.MAX_TOKENS["togethercomputer/m2-bert-80M-2k-retrieval"] = 2048
algo.MAX_TOKENS["togethercomputer/m2-bert-80M-8k-retrieval"] = 8192
algo.MAX_TOKENS["togethercomputer/m2-bert-80M-32k-retrieval"] = 32768
algo.MAX_TOKENS["WhereIsAI/UAE-Large-V1"] = 512
algo.MAX_TOKENS["BAAI/bge-large-en-v1.5"] = 512
algo.MAX_TOKENS["BAAI/bge-base-en-v1.5"] = 512
algo.MAX_TOKENS["sentence-transformers/msmarco-bert-base-dot-v5"] = 512
algo.MAX_TOKENS["bert-base-uncased"] = 512

current_model = os.environ.get("LLM_MODEL", "gpt-3.5-turbo-1106")
algo.MAX_TOKENS[current_model] = get_model_max_input(current_model)


# add new git provider
def get_git_provider():
    from pr_agent.config_loader import get_settings

    _git_provider_old_ = get_settings().config.git_provider
    get_settings().config.git_provider = "devchat"
    provider = _get_git_provider_old()
    get_settings().config.git_provider = _git_provider_old_
    return provider


import pr_agent.git_providers as git_providers

from merico.pr.providers.devchat_provider import DevChatProvider

git_providers._GIT_PROVIDERS["devchat"] = DevChatProvider
_get_git_provider_old = git_providers.get_git_provider
git_providers.get_git_provider = get_git_provider


from pr_agent.cli import run
from pr_agent.config_loader import get_settings

# mock logging method, to redirect log to IDE
from pr_agent.log import inv_analytics_filter, setup_logger


class CustomOutput:
    def __init__(self):
        pass

    def write(self, message):
        IDEService().ide_logging("info", message.strip())

    def flush(self):
        pass

    def close(self):
        pass


log_level = os.environ.get("LOG_LEVEL", "INFO")
logger = setup_logger(log_level)

logger.remove(None)
logger.add(
    CustomOutput(),
    level=logging.DEBUG,
    format="{message}",
    colorize=False,
    filter=inv_analytics_filter,
)


from merico.pr.config_util import (
    get_gitlab_host,
    get_repo_type,
    read_server_access_token_with_input,
    read_review_inline_config,
)
from merico.pr.custom_suggestions_config import get_custom_suggestions_system_prompt

# set openai key and api base
get_settings().set("OPENAI.KEY", os.environ.get("OPENAI_API_KEY", ""))
get_settings().set("OPENAI.API_BASE", os.environ.get("OPENAI_API_BASE", ""))
get_settings().set("LLM.CUSTOM_LLM_PROVIDER", "openai")


# set github token
access_token = read_server_access_token_with_input(sys.argv[1])
if not access_token:
    print("Command has been canceled.", flush=True)
    sys.exit(0)

repo_type = get_repo_type(sys.argv[1])
IDEService().ide_logging("debug", f"repo type: {repo_type}")
if repo_type == "github":
    get_settings().set("GITHUB.USER_TOKEN", access_token)
elif repo_type == "gitlab":
    get_settings().set("GITLAB.PERSONAL_ACCESS_TOKEN", access_token)
    host = get_gitlab_host(sys.argv[1])
    if host:
        IDEService().ide_logging("debug", f"gitlab host: {host}")
        get_settings().set("GITLAB.URL", host)
else:
    print(
        "Unsupported git hosting service, input pr url is:",
        sys.argv[1],
        file=sys.stderr,
        flush=True,
    )
    sys.exit(1)


# USER TOKEN

# set git provider, default is devchat
# in devchat provider, we will create actual repo provider
# get_settings().set("CONFIG.GIT_PROVIDER", "devchat")

# set model
get_settings().set("CONFIG.MODEL", os.environ.get("LLM_MODEL", "gpt-3.5-turbo-1106"))
get_settings().set("CONFIG.MODEL_TURBO", os.environ.get("LLM_MODEL", "gpt-3.5-turbo-1106"))
get_settings().set("CONFIG.FALLBACK_MODELS", [os.environ.get("LLM_MODEL", "gpt-3.5-turbo-1106")])

# disable help text as default config
get_settings().set("PR_REVIEWER.ENABLE_HELP_TEXT", False)
get_settings().set("PR_DESCRIPTION.ENABLE_HELP_TEXT", False)
get_settings().set("PR_DESCRIPTION.ENABLE_HELP_COMMENT", False)
get_settings().set("PR_CODE_SUGGESTIONS.ENABLE_HELP_TEXT", False)
get_settings().set("PR_TEST.ENABLE_HELP_TEXT", False)
get_settings().set("CHECKS.ENABLE_HELP_TEXT", False)
# get_settings().set("PR_CODE_SUGGESTIONS.SUMMARIZE", False)


# handle custom suggestions command
if sys.argv[2] == "custom_suggestions":
    get_settings().pr_code_suggestions_prompt.system = get_custom_suggestions_system_prompt()
    sys.argv[2] = "improve"

# get current language config
language = IDEService().ide_language()
language_prompt = "\n\n输出内容使用中文输出。\n" if language == "zh" else ""
get_settings().pr_code_suggestions_prompt.system += language_prompt
get_settings().pr_review_prompt.system += language_prompt
get_settings().pr_description_prompt.system += language_prompt
if read_review_inline_config():
    get_settings().pr_reviewer.inline_code_comments = True

# config for find similar issues
get_settings().set("PR_SIMILAR_ISSUE.VECTORDB", "lancedb")
get_settings().set("LANCEDB.URI", "data/lancedb")

# set git provider type, devchat provider will create actual repo provider based on this type
pr_provider_type = get_repo_type(sys.argv[1])
if not pr_provider_type:
    print(
        "Unsupported git hosting service, input pr url is:",
        sys.argv[1],
        file=sys.stderr,
        flush=True,
    )
    sys.exit(1)
get_settings().set("CONFIG.GIT_PROVIDER", pr_provider_type)
os.environ["CONFIG.GIT_PROVIDER_TYPE"] = pr_provider_type
# os.environ['ENABLE_PUBLISH_LABELS'] = "1"

if __name__ == "__main__":
    sys.argv = [sys.executable, "--pr_url", sys.argv[1].strip(), sys.argv[2].strip()]
    run()
