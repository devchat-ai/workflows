import os
import subprocess
import sys
import time

import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

# noqa: I001
from api.utils import (  # noqa: E402
    OPENAPI_URL,
    PROJECT_ID,
    SERVER_URL,
    VERSION_URL,
    get_path_op_id,
    session,
)

# noqa: E402
from lib.chatmark.step import Step  # noqa: E402


def get_apidocs():
    res = session.get(
        f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/apidocs",
        params={"page": 1, "size": 100},
    )
    return res.json()["docs"]


def delete_old_apidocs(apidocs):
    for apidoc in apidocs:
        session.delete(f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/apidocs/{apidoc['id']}")


def get_local_version():
    cmd = "git rev-parse HEAD"
    res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
    return res.stdout.decode("utf-8").strip()


def check_api_version():
    # 如果没有配置VERSION_URL，则跳过版本检查
    if not VERSION_URL:
        print("未配置VERSION_URL，跳过API版本检查...")
        return

    local_version = get_local_version()
    print("检查被测服务器文档是否已经更新到最新版本...")
    while True:
        try:
            res = session.get(VERSION_URL)
            version = res.json()["version"]
            if version == local_version:
                print(f"API 文档已更新，当前版本为 {version}，开始上传 OpenAPI 文档...")
                break
            else:
                print(
                    ".",
                    end="",
                    flush=True,
                )
                time.sleep(5)
        except Exception as e:
            print(f"检查 API 版本失败！{e}", flush=True)
            time.sleep(5)


def wait_for_testcase_done(testcase_id):
    while True:
        try:
            res = session.get(
                f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/testcases/{testcase_id}"
            )
            data = res.json()
            status = data["status"]
            if status == "content_ready":
                print("文本用例生成完成！", flush=True)
                break
            else:
                print(
                    ".",
                    end="",
                    flush=True,
                )
                time.sleep(5)
        except Exception as e:
            print(f"检查文本用例状态失败！{e}", flush=True)
            time.sleep(5)


def wait_for_testcode_done(task_id):
    while True:
        try:
            res = session.get(f"{SERVER_URL}/tasks/{task_id}")
            data = res.json()
            status = data["status"]
            if status == "succeeded":
                print("自动测试脚本生成完成！", flush=True)
                break
            else:
                print(
                    ".",
                    end="",
                    flush=True,
                )
                time.sleep(5)
        except Exception as e:
            print(f"检查自动测试脚本生成失败！{e}", flush=True)
            time.sleep(5)


def get_testcode(testcase_id):
    res = session.get(
        f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/testcodes",
        params={"testcase_id": testcase_id},
    )
    return res.json()["testcodes"][0]


def wait_for_task_done(task_id):
    while True:
        try:
            res = session.get(f"{SERVER_URL}/tasks/{task_id}")
            data = res.json()
            status = data["status"]
            if status == "succeeded":
                print("自动测试脚本执行完成！", flush=True)
                break
            else:
                print(
                    ".",
                    end="",
                    flush=True,
                )
                time.sleep(5)
        except Exception as e:
            print(f"检查自动测试脚本状态失败！{e}", flush=True)
            time.sleep(5)


def get_testcase(api_path_id):
    res = session.get(
        f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/testcases",
        params={"page": 1, "size": 100, "pathop_id": api_path_id},
    )
    return res.json()["testcases"][0]


def main():
    error_msg = "请输入要测试的API名称和测试目标！如：/test.api.upload api_path method test_target"
    if len(sys.argv) < 2:
        print(error_msg)
        return
    args = sys.argv[1].strip().split(" ")
    if len(args) < 3:
        print(error_msg)
        return
    api_path = args[0]
    method = args[1]
    test_target = " ".join(args[2:])
    docs = get_apidocs()
    with Step("检查 API 版本是否更新..."):
        check_api_version()
        delete_old_apidocs(docs)

    with Step(f"上传 OpenAPI 文档，并且触发 API {api_path} 的测试用例和自动测试脚本生成任务..."):
        # 使用配置的OPENAPI_URL
        if not OPENAPI_URL:
            print("错误：未配置OPENAPI_URL，无法获取OpenAPI文档")
            return

        res = requests.get(
            OPENAPI_URL,
        )
        res = session.post(
            f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/apidocs",
            files={"file": ("openapi.json", res.content, "application/json")},
            data={"apiauth_id": docs[0]["apiauth_id"]},
        )
        if res.status_code == 200:
            print("上传 OpenAPI 文档成功！\n")
        else:
            print(f"上传 OpenAPI 文档失败！{res.text}", flush=True)
            return
    apipathop_id = get_path_op_id(api_path, method)
    with Step("开始生成文本用例..."):
        res = session.post(
            f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/testcases",
            params={"generate_content": True},
            json={"apipathop_id": apipathop_id, "title": test_target},
        )
        if res.status_code == 200:
            print("提交生成文本用例成功！等待生成完成...", flush=True)
            testcase_id = res.json()["id"]
            wait_for_testcase_done(testcase_id)
        else:
            print(f"提交生成文本用例失败！{res.text}", flush=True)
            return
    with Step("开始生成自动测试脚本..."):
        res = session.post(
            f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/tasks/testcode",
            params={"testcase_id": testcase_id},
        )
        if res.status_code == 200:
            print("提交生成自动测试脚本成功！等待生成完成...", flush=True)
            task_id = res.json()["id"]
            wait_for_testcode_done(task_id)
        else:
            print(f"提交生成自动测试脚本失败！{res.text}", flush=True)
            return
    with Step("开始执行自动测试脚本..."):
        testcode = get_testcode(testcase_id)
        testcode_id = testcode["id"]
        res = session.post(
            f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/testcodes/{testcode_id}/exec",
        )
        if res.status_code == 200:
            print("提交执行自动测试脚本成功！", flush=True)
        else:
            print(f"提交执行自动测试脚本失败！{res.text}")
            return

    api_path_id = get_path_op_id(api_path, method)
    with Step("开始查询测试脚本执行结果..."):
        while True:
            res = session.get(
                f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/tasks",
                params={"page": 1, "size": 1},
            )
            ret = res.json()
            task = ret["tasks"][0]
            task_id = task["id"]
            wait_for_task_done(task_id)
            testcase = get_testcase(api_path_id)
            last_testcode_passed = testcase["last_testcode_passed"]
            if last_testcode_passed:
                print("测试脚本执行成功！", flush=True)
                break
            else:
                print("测试脚本执行失败！", flush=True)
                break


if __name__ == "__main__":
    main()
