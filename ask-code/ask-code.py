import os
import sys
import json
from chat.ask_codebase.chains.smart_qa import SmartQA

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "libs"))

from ide_services import get_lsp_brige_port


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
    print(answer[0])
    print(
        f"***/ask-code has costed approximately ${int(float(answer[2]['token_usage']['total_cost'])/0.7*10000)/10000} USD for this question.***"
    )


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
