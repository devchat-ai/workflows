import os
import sys

from lib.workflow.config import read_config, save_config

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from lib.workflow.common_util import editor  # noqa: E402


@editor(
    "Input the issues repository, "
    "If the issue is within this repository, no need to specify. "
    "Otherwise, format as: username/repository-name"
)
@editor(
    "Input your gitlab API URL to access gitlab api, if not specified, default is https://gitlab.com/api/v4"
)
@editor("Input your gitlab TOKEN to access gitlab api")
@editor("Input your gitlab work report template path")
def edit_config(issue_url, gitlab_api_url, gitlab_token, template_path):
    pass


def main():
    issue_url = read_config("git_issue_repo", is_global=True)
    gitlab_token = read_config("gitlab_token", is_global=True)
    gitlab_api_url = read_config("gitlab_api_url", is_global=True)
    template_path = read_config("gitlab_work_report_template_path", is_global=True)
    issue_url, gitlab_api_url, gitlab_token, template_path = edit_config(
        issue_url, gitlab_api_url, gitlab_token, template_path
    )
    if not gitlab_token:
        print("Please specify the gitlab token to access gitlab api.")
        sys.exit(0)
    save_config("git_issue_repo", issue_url, is_global=True)
    save_config("gitlab_token", gitlab_token, is_global=True)
    save_config("gitlab_api_url", gitlab_api_url, is_global=True)
    save_config("gitlab_work_report_template_path", template_path, is_global=True)

    print("config gitlab settings successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
