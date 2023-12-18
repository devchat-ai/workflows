import os
import sys
from chat.ask_codebase.chains.smart_qa import SmartQA

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "libs"))

from ide_services import get_lsp_brige_port  # noqa: E402


def query(question, lsp_brige_port):
    root_path = os.getcwd()

    # Create an instance of SmartQA
    smart_qa = SmartQA(root_path)

    # Use SmartQA to get the answer
    answer = smart_qa.run(
        question=question,
        verbose=False,
        dfs_depth=3,
        dfs_max_visit=10,
        bridge_url=f"http://localhost:{lsp_brige_port}",
    )

    # Print the answer
    # key is model name, value is (prompt_token_price, completion_token_price)
    prices = {
        "gpt-4": (0.03, 0.06),
        "gpt-4-32k": (0.06, 0.12),
        "gpt-3.5-turbo": (0.0015, 0.002),
        "gpt-3.5-turbo-16k": (0.003, 0.004),
        "claude-2": (0.01102, 0.03268),
        "starchat-alpha": (0.0004, 0.0004),
        "CodeLlama-34b-Instruct": (0.0008, 0.0008),
        "llama-2-70b-chat": (0.001, 0.001),
        "gpt-3.5-turbo-1106": (0.001, 0.002),
        "gpt-4-1106-preview": (0.01, 0.03),
        "gpt-4-1106-vision-preview": (0.01, 0.03),
        # if model not in above list, use this price
        "others": (0.001, 0.002),
    }
    print(answer[0])
    spent_money = 0.0
    token_usages = answer[2].get("usages", [])
    for token_usage in token_usages:
        price = prices.get(token_usage.model, prices["others"])
        spent_money += (price[0] * token_usage.prompt_tokens) / 1000 + (
            price[1] * token_usage.completion_tokens
        ) / 1000
    print(f"***/ask-code has costed approximately ${spent_money/0.7} USD for this question.***")


def main():
    try:
        if len(sys.argv) < 3:
            print("Usage: python index_and_query.py query [question] [port]")
            sys.exit(1)

        port = get_lsp_brige_port()

        question = sys.argv[2]
        query(question, port)
        sys.exit(0)
    except Exception as e:
        print("Exception: ", e, file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
