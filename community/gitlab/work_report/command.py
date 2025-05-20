import os
import sys
from datetime import datetime, timedelta

from devchat.llm import chat

from community.gitlab.git_api import (
    get_commit_author,
    get_repo,
    get_repo_commits,
    get_repo_issues,
    get_username,
)

PROMPT = """
我希望你根据以下信息生成一份从 {start_time} 到 {end_time} 的工作报告。

问题列表:
<issues>
{issues}
</issues>

提交列表:
<commits>
{commits}
</commits>

请参考以下模板内容的格式：
<template>
{template}
</template>
"""


def get_template():
    template_path = os.path.join(os.path.dirname(__file__), "template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def get_issues(start_time, end_time):
    name = get_username()
    issue_repo = get_repo(True)
    issues = get_repo_issues(
        issue_repo, name, state=None, created_after=start_time, created_before=end_time
    )
    return issues


def get_commits(start_time, end_time):
    name = get_commit_author()
    issue_repo = get_repo(False)
    commits = get_repo_commits(issue_repo, author=name, since=start_time, until=end_time)
    return commits


@chat(prompt=PROMPT, stream_out=True)
def generate_work_report(start_time, end_time, issues, commits, template):
    pass


def main():
    arg = sys.argv[1]
    args = arg.split(" ")
    if len(args) == 3:
        start_time = args[1]
        end_time = args[2]
    else:
        end_time = datetime.now().strftime("%Y-%m-%d")
        start_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    issues = get_issues(start_time, end_time)
    commits = get_commits(start_time, end_time)
    template = get_template()
    generate_work_report(
        start_time=start_time,
        end_time=end_time,
        issues=issues,
        commits=commits,
        template=template,
    )


if __name__ == "__main__":
    main()
