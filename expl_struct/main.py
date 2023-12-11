from typing import Optional
import os
import click

from chat.ask_codebase.assistants.directory_structure.repo_explainer import (
    RepoStructureExplainer,
)

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

    print("\n\n```Step\n# Analyzing codebase...\n", flush=True)
    answer = e.analyze(user_query=objective)
    print("Scanning complete.\n```", flush=True)

    print(f"\n{answer}\n", flush=True)


if __name__ == "__main__":
    main()
