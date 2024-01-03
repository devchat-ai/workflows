import sys
import os
import json
import requests


def get_script_path():
    """Return the directory path of the current script."""
    return os.path.dirname(__file__)


def update_sys_path():
    """Extend system path to include library directories."""
    libs_path = os.path.join(get_script_path(), "..", "..", "..", "libs")
    root_path = os.path.join(get_script_path(), "..", "..", "libs")
    sys.path.extend([libs_path, root_path])


update_sys_path()
from llm_api import chat_completion_stream  # noqa: E402


def load_commit_cache():
    """Load or initialize the commit cache."""
    try:
        cache_filepath = os.path.join(get_script_path(), "commit_cache.json")
        if not os.path.exists(cache_filepath):
            return {}
        with open(cache_filepath, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_commit_cache(commit_cache):
    """Save the commit cache to a JSON file."""
    try:
        cache_filepath = os.path.join(get_script_path(), "commit_cache.json")
        with open(cache_filepath, "w", encoding="utf-8") as cache_file:
            json.dump(commit_cache, cache_file)
    except IOError as e:
        print(f"Error saving commit cache: {e}")


def get_commit_diff(url, commit_cache):
    """Extract commit diff from the given URL."""
    parts = url.split("/")
    user = parts[3]
    repo = parts[4]
    commit_hash = parts[6]

    api_url = f"https://api.github.com/repos/{user}/{repo}/commits/{commit_hash}"

    for _1 in range(5):
        try:
            if commit_hash in commit_cache and "diff" in commit_cache[commit_hash]:
                return commit_cache[commit_hash]["diff"]
            response = requests.get(
                api_url,
                headers={"Accept": "application/vnd.github.v3.diff"},
                timeout=20,
            )

            if response.status_code == 200:
                if commit_hash not in commit_cache:
                    commit_cache[commit_hash] = {}
                commit_cache[commit_hash]["diff"] = response.text
                return response.text
        except Exception:
            continue
    raise Exception("Error: Unable to fetch the commit diff.")


def get_commit_messages():
    """Compose commit messages based on the provided commit URL."""
    commit_cache = load_commit_cache()
    if commit_cache is None:
        sys.exit(-1)
    prompt = sys.argv[1]
    context = json.loads(sys.argv[3])
    commit_url = context["vars"]["commit_url"]

    diff = get_commit_diff(commit_url, commit_cache)
    save_commit_cache(commit_cache)

    prompt = prompt.replace("{__USER_INPUT__}", "").replace("{__DIFF__}", diff)

    messages = [{"role": "user", "content": prompt}]
    response = chat_completion_stream(messages, {"model": "gpt-4-1106-preview"})

    print(response.get("content", "")) if response.get("content", "") else print(response)


if __name__ == "__main__":
    get_commit_messages()
