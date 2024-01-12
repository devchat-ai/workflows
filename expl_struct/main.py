import os
import sys
from typing import Optional

import click
from chat.ask_codebase.assistants.directory_structure.repo_explainer import (
    RepoStructureExplainer,
)

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))

from chatmark import Step  # noqa: E402

Languages = {
    "en": "English",
    "zh": "Chinese",
}


@click.command()
@click.argument("objective", required=False, default=None)
@click.option(
    "-lang",
    "--language",
    type=click.Choice(list(Languages.keys()), case_sensitive=False),
)
def main(objective: Optional[str], language: str):
    if not objective:
        objective = "Help me understand the structure of this repo."

    chat_lang = Languages.get(language, None)
    repo_path = os.getcwd()

    e = RepoStructureExplainer(root_path=repo_path, chat_language=chat_lang)

    with Step("Analyzing codebase..."):
        answer = e.analyze(user_query=objective)
        print("Done.", flush=True)

    print(f"\n{answer}\n", flush=True)


if __name__ == "__main__":
    main()
