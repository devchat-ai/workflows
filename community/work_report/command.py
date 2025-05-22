import os
from datetime import date

from devchat.llm import chat, chat_json

from community.github.git_api import is_github_repo

if is_github_repo():
    from community.github.git_api import (
        get_commit_author,
        get_github_repo as get_repo,
        get_repo_commits,
        get_repo_issues,
        get_github_username as get_username,
    )
else:
    from community.gitlab.git_api import (
        get_commit_author,
        get_repo,
        get_repo_commits,
        get_repo_issues,
        get_username,
    )
from lib.workflow.decorators import check_input


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


@chat(
    prompt="""
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
""",
    stream_out=True,
)
def generate_work_report(start_time, end_time, issues, commits, template):
    pass


@chat_json(
    prompt="""
今天是 {today}，我希望你根据输入信息获取开始时间和结束时间。
如果无法获取，则获取昨天到今天的时间范围。

<input>
{input}
</input>

输出格式为 JSON 格式，如下所示：
{{
    "start_time": "2025-05-19",
    "end_time": "2025-05-20"
}}
"""
)
def get_date_range(today, input):
    pass


@check_input("请输入需要生成工作报告的时间")
def main(input):
    result = get_date_range(today=date.today(), input=input)
    start_time = result["start_time"]
    end_time = result["end_time"]
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
