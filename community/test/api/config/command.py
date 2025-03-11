import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from lib.chatmark import Form, TextEditor  # 导入 ChatMark 组件


def read_global_config():
    """读取全局配置信息"""
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    
    server_url = config_data.get("api_testing_server_url", "")
    username = config_data.get("api_testing_server_username", "")
    password = config_data.get("api_testing_server_password", "")
    
    return server_url, username, password


def save_global_config(server_url, username, password):
    """保存全局配置信息"""
    config_path = os.path.join(os.path.expanduser("~/.chat"), ".workflow_config.json")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    
    config_data["api_testing_server_url"] = server_url
    config_data["api_testing_server_username"] = username
    config_data["api_testing_server_password"] = password
    
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def read_repo_config():
    """读取仓库相关配置信息"""
    config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    
    project_id = config_data.get("test_api_project_id", "")
    openapi_url = config_data.get("test_api_openapi_url", "")
    version_url = config_data.get("test_api_version_url", "")
    
    return project_id, openapi_url, version_url


def save_repo_config(project_id, openapi_url, version_url):
    """保存仓库相关配置信息"""
    config_path = os.path.join(os.getcwd(), ".chat", ".workflow_config.json")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    
    config_data["test_api_project_id"] = project_id
    config_data["test_api_openapi_url"] = openapi_url
    config_data["test_api_version_url"] = version_url
    
    with open(config_path, "w+", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def main():
    print("开始配置 API 测试所需的设置...", end="\n\n", flush=True)

    # 读取全局配置
    server_url, username, password = read_global_config()
    
    # 读取仓库配置
    project_id, openapi_url, version_url = read_repo_config()

    # 创建表单组件
    server_url_editor = TextEditor(server_url)
    username_editor = TextEditor(username)
    password_editor = TextEditor(password)
    project_id_editor = TextEditor(project_id)
    openapi_url_editor = TextEditor(openapi_url)
    version_url_editor = TextEditor(version_url)
    
    # 创建表单
    form = Form([
        "## DevChat API 测试服务器配置",
        "请输入服务器 URL (例如: http://kagent.merico.cn:8000):",
        server_url_editor,
        "请输入用户名:",
        username_editor,
        "请输入密码:",
        password_editor,
        "## 仓库配置",
        "请输入DevChat API 测试服务器中项目 ID (例如: 37):",
        project_id_editor,
        "请输入 OpenAPI URL (例如: http://kagent.merico.cn:8080/openapi.json):",
        openapi_url_editor,
        "请输入版本 URL (例如: http://kagent.merico.cn:8080/version)，不输入表示不需要检查服务器测试环境版本:",
        version_url_editor,
    ])
    
    # 渲染表单
    form.render()
    
    # 获取用户输入
    server_url = server_url_editor.new_text.strip()
    username = username_editor.new_text.strip()
    password = password_editor.new_text.strip()
    project_id = project_id_editor.new_text.strip()
    openapi_url = openapi_url_editor.new_text.strip()
    version_url = version_url_editor.new_text.strip()

    # 保存全局配置
    if server_url and username and password:
        save_global_config(server_url, username, password)
    else:
        print("请提供完整的全局配置信息 (SERVER_URL, USERNAME, PASSWORD)。")
        sys.exit(1)
    
    # 保存仓库配置
    if project_id and openapi_url and version_url:
        save_repo_config(project_id, openapi_url, version_url)
    else:
        print("请提供完整的仓库配置信息 (PROJECT_ID, OPENAPI_URL, VERSION_URL)。")
        sys.exit(1)

    print("\n配置信息已成功保存！")
    print(f"全局配置: SERVER_URL={server_url}, USERNAME={username}, PASSWORD={'*' * len(password)}")
    print(f"仓库配置: PROJECT_ID={project_id}, OPENAPI_URL={openapi_url}, VERSION_URL={version_url}")
    
    print("\n您现在可以使用其他 API 测试工作流了。")
    sys.exit(0)


if __name__ == "__main__":
    main()