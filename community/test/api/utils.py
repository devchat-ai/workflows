import os
import json
import requests
import sys
from lib.workflow.call import workflow_call

# 默认配置，仅在无法读取配置文件时使用


session = requests.Session()
_is_login = False

def read_config():
    """读取配置文件中的设置"""
    # 读取全局配置
    global_config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    global_config = {}
    if os.path.exists(global_config_path):
        try:
            with open(global_config_path, "r", encoding="utf-8") as f:
                global_config = json.load(f)
        except Exception:
            pass
    
    # 读取仓库配置
    repo_config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    repo_config = {}
    if os.path.exists(repo_config_path):
        try:
            with open(repo_config_path, "r", encoding="utf-8") as f:
                repo_config = json.load(f)
        except Exception:
            pass
    
    # 获取配置值
    server_url = global_config.get("api_testing_server_url", "")
    username = global_config.get("api_testing_server_username", "")
    password = global_config.get("api_testing_server_password", "")
    project_id = repo_config.get("test_api_project_id", "")
    openapi_url = repo_config.get("test_api_openapi_url", "")
    version_url = repo_config.get("test_api_version_url", "")
    
    return server_url, username, password, project_id, openapi_url, version_url

def ensure_config():
    """确保配置存在，如果不存在则调用配置工作流"""
    global_config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    repo_config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    
    # 检查全局配置和仓库配置是否存在
    global_config_exists = os.path.exists(global_config_path)
    repo_config_exists = os.path.exists(repo_config_path)
    
    # 检查必填配置项是否存在
    config_valid = True
    if global_config_exists and repo_config_exists:
        # 读取配置
        global_config = {}
        repo_config = {}
        try:
            with open(global_config_path, "r", encoding="utf-8") as f:
                global_config = json.load(f)
            with open(repo_config_path, "r", encoding="utf-8") as f:
                repo_config = json.load(f)
        except Exception:
            config_valid = False
        
        # 检查必填项
        if (not global_config.get("api_testing_server_url") or
            not global_config.get("api_testing_server_username") or
            not global_config.get("api_testing_server_password") or
            not repo_config.get("test_api_project_id") or
            not repo_config.get("test_api_openapi_url")):
            config_valid = False
    else:
        config_valid = False
    
    if not config_valid:
        print("缺少API测试所需的配置，将启动配置向导...")
        workflow_call("/test.api.config")
        
        # 重新检查配置是否已创建并包含必要项
        try:
            if os.path.exists(global_config_path) and os.path.exists(repo_config_path):
                with open(global_config_path, "r", encoding="utf-8") as f:
                    global_config = json.load(f)
                with open(repo_config_path, "r", encoding="utf-8") as f:
                    repo_config = json.load(f)
                
                if (global_config.get("api_testing_server_url") and
                    global_config.get("api_testing_server_username") and
                    global_config.get("api_testing_server_password") and
                    repo_config.get("test_api_project_id") and
                    repo_config.get("test_api_openapi_url")):
                    return True
            print("配置失败")
            return False
        except Exception:
            print("配置失败")
            return False
    
    return True

# 读取配置
result = ensure_config()
if not result:
    print("配置失败，工作流不能继续执行")
    exit(0)
SERVER_URL, USERNAME, PASSWORD, PROJECT_ID, OPENAPI_URL, VERSION_URL = read_config()

def login():
    global _is_login
    if _is_login:
        return
    session.post(
        f"{SERVER_URL}/user/auth/login",
        data={"username": USERNAME, "password": PASSWORD, "grant_type": "password"},
    )
    _is_login = True


def get_path_op_id(keyword: str, method: str):
    res = session.get(
        f"{SERVER_URL}/autotest/projects/{PROJECT_ID}/apipathops",
        params={"keyword": keyword, "page": 1, "size": 20},
    )
    for pathop in res.json()["pathops"]:
        if pathop["method"].lower().strip() == method.lower().strip():
            return pathop["id"]


login()