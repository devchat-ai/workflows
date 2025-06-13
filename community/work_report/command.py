import datetime
import json

import requests
from requests.auth import HTTPBasicAuth

from lib.chatmark.step import Step

GITLAB_TOKEN = "xxx"
GITLAB_URL = "xx"
GITLAB_HEADERS = {"Authorization": f"Bearer {GITLAB_TOKEN}"}
GITLAB_USERS = ["xxx"]

JIRA_TOKEN = "xxx"
JIRA_USERNAME = "xxx"
JIRA_URL = "xxx"
JIRA_DEV_USER = "xxx"
JIRA_API_VERSION = "2"

OPENAI_API_URL = "xxx"
OPENAI_API_KEY = "xxx"
LLM_MODEL = "xxx"

START_TIME = datetime.datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S")
END_TIME = datetime.datetime.strptime("2025-06-11 23:59:59", "%Y-%m-%d %H:%M:%S")

# ISSUE关联关系，如何查找？
MATCH_ISSUE_BY = "ai"  # 可选值: "branch", "commit", "mr", "ai"


# TODO
# 1. 对于COMMIT，MR，JIRA ISSUE的关联关系，使用脚本解析实现，例子中按我们的关联关系进行解析，客户现场根据客户情况进行调整修改；（已完成）
# 2. 提交所在分支，是否可以获取到？分支可能存在与ISSUE关联的信息；（不能，一般 MR 分支名称与 ISSUE 关联）
# 3. 针对同一个分支下时间范围内容的提交，生成提交语义总结以及复杂度（针对用户现场提交描述过于简化、以及客户希望识别修改的复杂度）；输入：启始提交与结束提交DIFF，关联ISSUE描述， 输出：修改语义总结，以及修改复杂度评估；
#        提交将被分为不同的语义块，一个语义块针对一组提交，描述了具体完成的修改功能等；
#        ISSUE会与语义块进行关联，将关联后的数据信息发送给AI，AI可以描述针对这个ISSUE，指定时间完成了什么内容；（这个不太懂什么意思）
# 4. MR与ISSUE需要关联，MR的发布，与MR合并，对于ISSUE来说，是重要的状态变化，需要被关注；（已完成）
# 4. JIRA ISSUE查询时，除了获取约定时间范围内更新的ISSUE，还需要获取提交关联的ISSUE，可能存在提交与ISSUE关联，但没有更新的情况；(这个好像没办法获取)
# 5. 用户对MR的评论或者REVIEW APPROVAL也应该被识别，作为用户的工作活动一部分；(已完成)


def get_user_id_by_email(email):
    """通过邮箱查找用户ID"""
    url = f"{GITLAB_URL}/api/v4/users"
    params = {"search": email, "per_page": 10}

    response = requests.get(url, headers=GITLAB_HEADERS, params=params)

    print(response.status_code)
    print(response.text)
    users = response.json()
    for user in users:
        if user.get("email") == email:  # 精确匹配邮箱
            return user.get("id")

    return None  # 如果未找到用户


def get_projects_by_email(email):
    """通过邮箱获取用户的项目"""
    user_id = get_user_id_by_email(email)

    if not user_id:
        print("获取用户ID失败")
        return "", []  # 未找到用户
    print("用户ID：", user_id, flush=True)

    # 使用用户ID获取项目
    # url = f"{GITLAB_URL}/api/v4/users/{user_id}/projects"
    # params = {
    #     "active": True,
    #     "last_activity_after": START_TIME,
    #     "order_by": "last_activity_at",
    #     "sort": "desc",
    #     "per_page": 50,
    #     "page": 1
    # }
    url = f"{GITLAB_URL}/api/v4/users/{user_id}/events"
    params = {"per_page": 100}

    response = requests.get(url, headers=GITLAB_HEADERS, params=params)

    events = response.json()
    print("events: ", len(events), flush=True)
    print(json.dumps(events, indent=2, ensure_ascii=False))

    events_recent = []
    for event in events:
        updated_time = datetime.datetime.fromisoformat(event["created_at"])
        updated_time = updated_time.replace(tzinfo=None)

        # 判断是否在时间范围内
        is_in_range = START_TIME <= updated_time <= END_TIME
        if is_in_range:
            events_recent.append(event)

    print("recent events:", len(events_recent), flush=True)
    projects = []
    project_ids = list(set([event["project_id"] for event in events_recent]))

    for id in project_ids:
        # 通过ID获取项目名称
        project_url = f"{GITLAB_URL}/api/v4/projects/{id}"
        project_response = requests.get(project_url, headers=GITLAB_HEADERS)

        if project_response.status_code == 200:
            project_data = project_response.json()
            project_name = project_data.get("name", "")
            projects.append({"name": project_name, "id": id})
        else:
            print(f"获取项目ID {id} 的信息失败: {project_response.status_code}")
            projects.append({"name": "未知项目", "id": id})
    print(json.dumps(projects, indent=2, ensure_ascii=False))
    return user_id, projects


def get_gitlab_projects():
    url = f"{GITLAB_URL}/api/v4/projects"
    params = {
        "membership": True,
        "active": True,
        "last_activity_after": START_TIME,
        "order_by": "last_activity_at",
        "sort": "desc",
        "per_page": 50,
        "page": 1,
    }
    response = requests.get(
        url,
        headers=GITLAB_HEADERS,
        params=params,
    )
    return response.json()


def get_merge_request_comments(project_id, merge_request_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/comments"
    response = requests.get(url, headers=GITLAB_HEADERS)
    return response.json()


def get_merge_request_approvals(project_id, merge_request_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/approvals"
    response = requests.get(url, headers=GITLAB_HEADERS)
    return response.json()


def get_merge_request_commits(project_id, merge_request_iid):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests/{merge_request_iid}/commits"
    response = requests.get(url, headers=GITLAB_HEADERS)
    return response.json()


def get_merge_requests(projects, user_id):
    merge_requests = []
    for project in projects:
        print(f"正在处理项目: {project['name']} (ID: {project['id']})")
        project_id = project["id"]
        url = f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests"
        params = {
            "author_id": user_id,
            "updated_after": START_TIME,
            "updated_before": END_TIME,
        }
        response = requests.get(url, headers=GITLAB_HEADERS, params=params)
        data = response.json()
        ret = []
        for item in data:
            ret.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "description": item["description"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                    "closed_at": item["closed_at"],
                    "closed_by": item["closed_by"],
                    "draft": item["draft"],
                    "has_conflicts": item["has_conflicts"],
                    "merged_at": item["merged_at"],
                    "merged_by": item["merged_by"],
                    "reviewers": item["reviewers"],
                    "source_branch": item["source_branch"],
                    "state": item["state"],
                    "comments": get_merge_request_comments(project_id, item["iid"]),
                    "approvals": get_merge_request_approvals(project_id, item["iid"]),
                    "commits": get_merge_request_commits(project_id, item["iid"]),
                }
            )
        if not ret:
            continue
        merge_requests.append(
            {
                "project_name": project["name"],
                "project_id": project_id,
                "merge_requests": ret,
            }
        )
    return merge_requests


def get_diff(project_id, issues, from_commit, to_commit, commits_message):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/compare"
    headers = {"Authorization": f"Bearer {GITLAB_TOKEN}"}
    from_commit += "^"
    params = {"from": from_commit, "to": to_commit}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    prompt = f"""
    你是一个经验丰富的编程助手，请根据ISSUE信息，以及对应提交的代码修改，生成一个用于日报、周报任务总结的工作描述与复杂度评估，重点是清晰、准确的将清楚针对ISSUE任务，具体做了哪些工作，太要涉及太多代码细节，因为日报、周报不需要设计太多代码细节。
    复杂度评估需要给出一个0-10的分值，0表示没有复杂度，10表示非常复杂。越复杂，表示处理实现需要的时间越长，难度越大。

    ISSUES内容如下：
    {json.dumps(issues, indent=2, ensure_ascii=False)}

    提交DIFF内容如下：
    {data}

    相关提交描述信息如下：
    {json.dumps(commits_message, indent=2, ensure_ascii=False)}

    只输出DIFF代码完成的具体工作内容，不要输出额外的解释。
    当前具体实现的工作内容有：
    """
    return ask_ai(prompt)


def is_merge_commit(commit):
    return len(commit["parent_ids"]) > 1


def get_commits(projects, author_email):
    commits = []
    for project in projects:
        print(f"正在处理项目: {project['name']} (ID: {project['id']})")
        project_id = project["id"]
        url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/commits"
        headers = {"Authorization": f"Bearer {GITLAB_TOKEN}"}
        params = {"since": START_TIME, "until": END_TIME, "all": True}
        response = requests.get(url, headers=headers, params=params)
        project_commits = response.json()

        # 根据用户邮箱过滤提交
        project_commits = [
            commit for commit in project_commits if commit["author_email"] == author_email
        ]

        # 过滤掉合并提交
        if project_commits:
            project_commits = list(filter(lambda x: not is_merge_commit(x), project_commits))

        if not project_commits:
            continue

        commits.append(
            {"project_name": project["name"], "project_id": project_id, "commits": project_commits}
        )
    return commits


def get_jira_projects():
    # 获取当前用户信息
    # myself = requests.get(
    #     f"{JIRA_URL}/rest/api/{JIRA_API_VERSION}/myself",
    #     auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_TOKEN)
    # ).json()

    # 获取与当前用户相关的项目
    url = f"{JIRA_URL}/rest/api/{JIRA_API_VERSION}/search"
    jql = f"assignee = '{JIRA_DEV_USER}' OR watcher = '{JIRA_DEV_USER}'"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_TOKEN),
        params={
            "jql": jql,
            "maxResults": 1000,
            "fields": "project",  # 只返回项目信息
        },
    )

    # 提取唯一的项目，使用字典而不是集合
    projects = {}
    for issue in response.json()["issues"]:
        project = issue["fields"]["project"]
        project_key = project["key"]
        if project_key not in projects:
            projects[project_key] = {
                "key": project_key,
                "name": project.get("name"),
                "id": project.get("id"),
                # 可以添加其他项目属性
            }

    # 返回项目列表
    return {"values": list(projects.values())}


def get_jira_issues(projects):
    """获取JIRA项目统计信息"""
    url = f"{JIRA_URL}/rest/api/{JIRA_API_VERSION}/search"
    result = {}

    for project in projects:
        project_id = project["id"]
        print(f"正在处理项目: {project['name']} (ID: {project_id})")
        # 1-4: 只需要统计数量的查询
        # stats_queries = {
        #     "total_issues": f"project = {project_id}",
        #     "user_issues": f"project = {project_id} AND assignee = '{JIRA_USERNAME}'",
        #     "open_issues": f"project = {project_id} AND status not in (无效的, 已关闭, 已完成, 暂不修改, Done, Closed)",
        #     "user_open_issues": f"project = {project_id} AND status not in (无效的, 已关闭, 已完成, 暂不修改, Done, Closed) AND assignee = '{JIRA_USERNAME}'",
        # }

        # stats = {}
        # for stat_name, jql in stats_queries.items():
        #     response = requests.get(
        #         url,
        #         params={"jql": jql, "maxResults": 1000},
        #         auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_TOKEN),
        #     )
        #     assert response.status_code == 200, f"获取JIRA统计信息失败: {response.status_code}, {response.text}"
        #     stats[stat_name] = response.json()["total"]

        # # 5. 获取项目指定时间内的更新ISSUE详情
        # updated_issues_params = {
        #     "jql": f"""project = {project_id} AND
        #     updated >= '{START_TIME.strftime("%Y-%m-%d %H:%M")}' AND
        #     updated <= '{END_TIME.strftime("%Y-%m-%d %H:%M")}'""",
        #     "startAt": 0,
        #     "maxResults": 1000,
        #     "expand": "changelog",
        # }
        # updated_response = requests.get(
        #     url,
        #     params=updated_issues_params,
        #     auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_TOKEN),
        # )
        # updated_issues = updated_response.json()["issues"]

        # 6. 获取用户指定时间内的更新ISSUE详情
        user_updated_issues_params = {
            "jql": f"""project = {project_id} AND
            updated >= '{START_TIME.strftime("%Y-%m-%d %H:%M")}' AND
            updated <= '{END_TIME.strftime("%Y-%m-%d %H:%M")}' AND
            assignee = '{JIRA_USERNAME}'""",
            "startAt": 0,
            "maxResults": 1000,
            "expand": "changelog",
        }
        user_updated_response = requests.get(
            url,
            params=user_updated_issues_params,
            auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_TOKEN),
        )
        user_updated_issues = user_updated_response.json()["issues"]

        # 对数据进行压缩处理，删除无效的字段
        for issue in user_updated_issues:
            issue.pop("fields", None)
            if "changelog" in issue:
                filtered_histories = []
                for history in issue["changelog"].get("histories", []):
                    author = history.get("author", {})
                    if "emailAddress" in author and author["emailAddress"] == JIRA_USERNAME:
                        author.pop("avatarUrls", None)
                        filtered_histories.append(history)
                issue["changelog"]["histories"] = filtered_histories

        # 存储项目统计结果
        result[project["name"]] = {
            # **stats,
            "user_updated_issues": user_updated_issues,
            # "updated_issues_count": len(updated_issues),
            "user_updated_issues_count": len(user_updated_issues),
        }

        # 打印项目统计信息
        print(f"\n项目 {project['name']} 统计信息:")
        # print(f"1. 总ISSUE数: {stats['total_issues']}")
        # print(f"2. 隶属用户的ISSUE数: {stats['user_issues']}")
        # print(f"3. 总OPEN状态的ISSUE数: {stats['open_issues']}")
        # print(f"4. 隶属用户OPEN状态的ISSUE数: {stats['user_open_issues']}")
        # print(f"5. 项目指定时间内总更新ISSUE数: {len(updated_issues)}")
        print(f"6. 用户指定时间内总更新ISSUE数: {len(user_updated_issues)}")
        print(
            f"7. 用户指定时间内更新ISSUE详情: {json.dumps(user_updated_issues, indent=2, ensure_ascii=False)}"
        )

    return result, user_updated_issues


def gen_report(relations):
    prompt = f"""
    你是一个经验丰富的助手，请根据以下数据，分析我的工作情况，并给出我的工作总结。
    数据如下：
    - 数据启始结束时间: {str(START_TIME)} - {str(END_TIME)}
    - 用户相关数据：
    {json.dumps(relations, indent=2, ensure_ascii=False)}

    输出有以下要求：
    1. 如果 issue 没有和提交相互关联，需要给出警告
    2. 以日报的形式去展现，包括当前开发者在指定范围内任务的具体执行完成情况、以及指定时间范围内提交代码工作的复杂度评估
    3. 日报中关于工作进展，主要优先依据代码提交描述，因为这个工作更体现时间范围内的具体工作进展
    4. 日报需要以 markdown 的形式输出
    5. 日报需要以中文输出
    6. 不要输入额外的解释，直接输出日报

    具体输出格式内容如下：
```report
# <姓名> <报告启始时间> - <报告结束时间>

# <项目名称> 任务进展
## <任务名称>
- **状态**: <任务状态> <emoji>
- **进展**:
  - <任务进展描述>
- **关联PR**: <关联的PR链接> (<PR状态>)
- **复杂度评估**: <复杂度评分> (0-10)
- **关联提交**:
  - <提交ID1> (<提交信息>)
- **关联JIRA ISSUE**: <JIRA ISSUE链接> (<JIRA ISSUE状态>)


## 注意信息
<根据数据，提出必要的注意信息，例如未关联的提交、需要关注的任务等，没有必须信息时，可以不输出此部分内容>
```
    """
    return ask_ai(prompt)


def ask_ai(prompt):
    response = requests.post(
        OPENAI_API_URL,
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model": LLM_MODEL, "messages": [{"role": "user", "content": prompt}]},
    )
    print("----> call llm")
    response = response.json()["choices"][0]["message"]["content"]
    print("<<---- ")
    return response


def get_commit_refs(project_id, commit_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/commits/{commit_id}/refs"
    print("获取提交引用的URL:", url)
    params = {"type": "branch"}
    response = requests.get(url, headers=GITLAB_HEADERS, params=params)
    return response.json()


def parse_issue_id_from_branch(branch_name):
    return branch_name


def parse_issue_id_from_commit_message(commit_message):
    assert False, "Need to implement a function to parse issue ID from commit message"


def parse_issue_id_from_mr(mr):
    assert False, "Need to implement a function to parse issue ID from merge request"


def identify_jira_issues(branch_name, commit_messages, mr_message):
    prompt = f"""
    你是一个经验丰富的助手，请识别出分支名称、提交消息、MR消息中绑定的JIRA ISSUE ID。
    分支名称: {branch_name}

    提交消息:
    {json.dumps(commit_messages, indent=2, ensure_ascii=False)}

    MR消息: {mr_message}

    输出结果为markdown JSON格式，具体如下：
    ```json
    ["jira_issue_id1", "jira_issue_id2", ...]
    ```
    """

    response = ask_ai(prompt)
    print(f"识别关联的ISSUE为：\n{response}")
    if response.find("```json") >= 0:
        index = response.find("```json")
        response = response[index + 7 :]
    if response.find("```") > 0:
        index = response.find("```")
        response = response[:index]
    print(f"识别关联的ISSUE2为：\n{response}")
    return json.loads(response)


def mr_commits_to_issue(project_id, mr, commits, jira_issues):
    if mr:
        source_branch = mr["source_branch"]
    else:
        # 通过提交找到分支
        source_branch = None
        for commit in commits:
            commit_id = commit["id"]
            branches = get_commit_refs(project_id, commit_id)
            print(branches)
            if len(branches) == 1:
                source_branch = branches[0]["name"]
                break
            elif len(branches) > 1:
                source_branch = branches[0]["name"]
    if not source_branch:
        print("无法找到源分支，请检查提交或合并请求")
        print("mr:", mr)
        print("commits:", [commit["id"] for commit in commits])
        print("项目ID:", project_id)
    else:
        print("源分支:", source_branch)
    issues = []
    if MATCH_ISSUE_BY == "branch":
        if source_branch:
            issue_id = parse_issue_id_from_branch(source_branch)
            print("解析到的分支中的JIRA ISSUE ID:", issue_id)
            if issue_id:
                issues.append(issue_id)
    elif MATCH_ISSUE_BY == "commit":
        for commit in commits:
            issue_id = parse_issue_id_from_commit_message(commit["message"])
            if issue_id:
                issues.append(issue_id)
    elif MATCH_ISSUE_BY == "mr" and mr:
        issue_id = parse_issue_id_from_mr(mr["message"])
        if issue_id:
            issues.append(issue_id)
    else:
        issues = identify_jira_issues(
            source_branch, [commit["message"] for commit in commits], mr["message"] if mr else ""
        )

    # 过滤重复的issue ID
    issues = list(set(issues))

    # 通过ISSUE ID获取JIRA ISSUE详情
    if not issues:
        # assert False, "无法从分支、提交或合并请求中解析出JIRA ISSUE ID"
        return []

    issues_new = []
    for issue_id in issues:
        # if issue_id in [issue["key"] for issue in jira_issues]:
        #     issues_new.append([issue for issue in jira_issues if issue["key"] == issue_id][0])
        #     print(f"已找到JIRA ISSUE {issue_id} 的详情")
        #     continue

        url = f"{JIRA_URL}/rest/api/{JIRA_API_VERSION}/issue/{issue_id}"
        response = requests.get(url, auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_TOKEN))
        if response.status_code == 200:
            issue_data = response.json()

            if "fields" in issue_data:
                issue_data_fields = issue_data["fields"]
                fields_pops = []
                for filed in issue_data_fields:
                    if issue_data_fields[filed] is None:
                        fields_pops.append(filed)
                for field in fields_pops:
                    issue_data_fields.pop(field)

                if "worklog" in issue_data_fields and "worklogs" in issue_data_fields["worklog"]:
                    filtered_worklogs = []
                    for worklog in issue_data_fields["worklog"]["worklogs"]:
                        # 比较时间
                        updated_time = datetime.datetime.fromisoformat(worklog["updated"])
                        updated_time = updated_time.replace(tzinfo=None)

                        # 判断是否在时间范围内
                        is_in_range = START_TIME <= updated_time <= END_TIME

                        if is_in_range:
                            filtered_worklogs.append(worklog)
                    issue_data_fields["worklog"]["worklogs"] = filtered_worklogs

                if "comment" in issue_data_fields and "comments" in issue_data_fields["comment"]:
                    filtered_comments = []
                    for comment in issue_data_fields["comment"]["comments"]:
                        # 比较时间
                        updated_time = datetime.datetime.fromisoformat(comment["updated"])
                        updated_time = updated_time.replace(tzinfo=None)

                        # 判断是否在时间范围内
                        is_in_range = START_TIME <= updated_time <= END_TIME

                        if is_in_range:
                            filtered_comments.append(comment)
                    issue_data_fields["comment"]["comments"] = filtered_comments

            issues_new.append(issue_data)
        else:
            print(f"无法获取JIRA ISSUE {issue_id} 的详情: {response.status_code}")

    return issues_new


def get_relation(merge_requests, commits, jira_issues):
    ret = []

    projects = {}
    for project in merge_requests:
        projects[project["project_id"]] = project["project_name"]
    for project in commits:
        projects[project["project_id"]] = project["project_name"]
    print(f"所有项目信息：\n{json.dumps(projects, indent=2, ensure_ascii=False)}")

    for iter_proj_id in projects:
        iter_proj_name = projects[iter_proj_id]
        print(f"当前处理项目：{iter_proj_name} {iter_proj_id}")

        project_commits = []
        for commit in commits:
            if commit["project_id"] == iter_proj_id:
                project_commits = commit["commits"]
                break
        print(f"项目提交：\n{json.dumps(project_commits, indent=2, ensure_ascii=False)}")

        project = None
        for proj in merge_requests:
            if proj["project_id"] == iter_proj_id:
                project = proj
                break

        if project:
            for mr in project["merge_requests"]:
                commits_in_mr = mr["commits"]

                project_commits = [
                    commit
                    for commit in project_commits
                    if commit["id"] not in [c["id"] for c in commits_in_mr]
                ]

                print("id:", project["project_id"])
                issues = mr_commits_to_issue(
                    project_id=project["project_id"],
                    mr=mr,
                    commits=commits_in_mr,
                    jira_issues=jira_issues,
                )
                ret.append(
                    {
                        "jira_issues": issues,
                        "merge_request": mr,
                        "project_name": project["project_name"],
                        "porject_id": project["project_id"],
                        "commits": commits_in_mr,
                    }
                )

        # 过滤掉没有分支的提交
        if project_commits:
            project_commits_new = []
            for commit in project_commits:
                if len(get_commit_refs(iter_proj_id, commit["id"])) > 0:
                    project_commits_new.append(commit)
                else:
                    print(f"存在提交没有分支：\n{json.dumps(commit, indent=2, ensure_ascii=False)}")
            project_commits = project_commits_new

        # 根据commits的连续性，进行分组
        groups = []
        if project_commits:
            # 创建一个映射，用于快速查找commit
            print(f"当前提交列表：\n{json.dumps(project_commits, indent=2, ensure_ascii=False)}")

            issues = identify_jira_issues("", [commit["message"] for commit in project_commits], "")

            # 找出所有的根提交（其父提交不在当前提交列表中的提交）
            all_commit_ids = {commit["id"] for commit in project_commits}
            root_commits = []
            commit_issues = {}

            for commit in project_commits:
                current_commit_message = commit["message"]
                current_commit_issue = None
                for issue in issues:
                    if current_commit_message.find(issue) >= 0:
                        current_commit_issue = issue
                        break
                commit_issues[commit["id"]] = current_commit_issue

            for commit in project_commits:
                # 检查该提交的所有父提交是否都不在当前提交列表中
                is_root = False
                for parent_id in commit["parent_ids"]:
                    all_not_in_commits_list = parent_id not in all_commit_ids
                    diff_issues = False
                    if commit_issues.get(parent_id, "") != commit_issues.get(commit["id"], ""):
                        diff_issues = True
                    if all_not_in_commits_list or diff_issues:
                        is_root = True
                        break

                # 如果没有父提交，也视为根提交
                if is_root or not commit["parent_ids"]:
                    root_commits.append(commit)

            # 确保所有提交都被分配到某个组
            assigned_commits = set()

            # 从每个根提交开始，构建提交链
            for root_commit in root_commits:
                if root_commit["id"] in assigned_commits:
                    continue

                current_group = [root_commit]
                assigned_commits.add(root_commit["id"])

                # 使用广度优先搜索找出所有相关的提交
                queue = [root_commit["id"]]
                while queue:
                    current_id = queue.pop(0)

                    # 查找以current_id为父提交的所有子提交
                    for commit in project_commits:
                        if commit["id"] in [root_commit["id"] for root_commit in root_commits]:
                            continue
                        if (
                            current_id in commit["parent_ids"]
                            and commit["id"] not in assigned_commits
                        ):
                            current_group.append(commit)
                            assigned_commits.add(commit["id"])
                            queue.append(commit["id"])

                # 添加构建好的提交链到分组中
                if current_group:
                    groups.append(current_group)

            # 检查是否有未分配的提交
            unassigned = [c for c in project_commits if c["id"] not in assigned_commits]
            if unassigned:
                groups.append(unassigned)

            # 为每个分组处理JIRA关联
            print(f"提交分组:\n{json.dumps(groups, indent=2, ensure_ascii=False)}")
            for group in groups:
                issues = mr_commits_to_issue(
                    project_id=iter_proj_id,
                    mr=None,
                    commits=group,
                    jira_issues=jira_issues,
                )

                ret.append(
                    {
                        "jira_issues": issues,
                        "merge_request": None,
                        "project_name": iter_proj_name,
                        "porject_id": iter_proj_id,
                        "commits": group,
                    }
                )

    return ret


def update_description_by_commits(relations):
    for relation in relations:
        issues = relation["jira_issues"]
        commits = relation["commits"]
        if not commits:
            continue

        # sort commits by date
        commits.sort(key=lambda x: x["created_at"])

        # 过滤不在指定时间范围内的提交
        filtered_commits = []
        for commit in commits:
            try:
                # Try the standard format first
                commit_date = datetime.datetime.strptime(
                    commit["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )
            except ValueError:
                try:
                    # Try the format with timezone offset
                    commit_date = datetime.datetime.strptime(
                        commit["created_at"].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f"
                    )
                except ValueError:
                    try:
                        # Try another possible format
                        commit_date = datetime.datetime.strptime(
                            commit["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                        )
                    except ValueError:
                        # If all formats fail, print the problematic date and skip
                        print(f"Skipping commit with unparseable date: {commit['created_at']}")
                        continue

            if START_TIME <= commit_date <= END_TIME:
                filtered_commits.append(commit)

        commits = filtered_commits
        if not commits:
            continue

        commits_message = [commit["message"] for commit in commits]

        from_commit = commits[0]["id"]
        to_commit = commits[-1]["id"]
        desc = get_diff(relation["porject_id"], issues, from_commit, to_commit, commits_message)
        relation["description"] = desc


def main():
    print("------", flush=True)
    for GITLAB_USER in GITLAB_USERS:
        with Step(f"正在生成用户{GITLAB_USER}的报告..."):
            user_id, projects = get_projects_by_email(GITLAB_USER)
            print(projects)
            print("获取到的GITLAB项目数量:", len(projects))
            if not projects:
                print("用户项目数为0，不符合预期。")
                exit(1)
            print("获取到的用户信息", flush=True)
            merge_requests = get_merge_requests(projects, user_id)
            print("获取到的合并请求数量:", len(merge_requests), flush=True)
            print(
                "合并请求详情:",
                json.dumps(merge_requests, indent=2, ensure_ascii=False),
                flush=True,
            )
            commits = get_commits(projects, GITLAB_USER)
            print(
                "获取到的提交数量:", sum(len(project["commits"]) for project in commits), flush=True
            )
            print("提交详情:", json.dumps(commits, indent=2, ensure_ascii=False), flush=True)
            jira_projects = get_jira_projects()
            print("获取到的JIRA项目数量:", len(jira_projects["values"]), flush=True)
            jira_issues, user_updated_issues = get_jira_issues(jira_projects["values"])
            print(
                "获取到的JIRA ISSUE数量:",
                sum(issue["user_updated_issues_count"] for issue in jira_issues.values()),
                flush=True,
            )
            relations = get_relation(merge_requests, commits, user_updated_issues)
            update_description_by_commits(relations)
            print("获取到的关联关系数量:", len(relations), flush=True)
            print("关联关系详情:", json.dumps(relations, indent=2, ensure_ascii=False), flush=True)
            print("生成日报...", flush=True)
            result = gen_report(relations)
            with open("result.md", "a") as f:
                f.write(result)
    print("日报已生成，保存在 result.md 文件中。")


if __name__ == "__main__":
    main()
