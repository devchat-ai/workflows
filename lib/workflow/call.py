import os
import re
import subprocess
import sys

import yaml

import __main__


def find_workflow_script(command_name: str) -> str:
    """
    根据命令名称查找对应的工作流脚本路径

    Args:
        command_name: 工作流命令名称，如 "github.commit"

    Returns:
        找到的脚本路径，如果未找到则返回空字符串
    """
    # 工作流目录优先级: custom > community > merico
    workflow_base_dirs = [
        os.path.expanduser("~/.chat/scripts/custom"),
        os.path.expanduser("~/.chat/scripts/community"),
        os.path.expanduser("~/.chat/scripts/merico"),
    ]

    # 解析命令名称，处理子命令
    parts = command_name.split(".")

    for base_dir in workflow_base_dirs:
        # 检查custom目录下是否有config.yml定义命名空间
        if base_dir.endswith("/custom"):
            config_path = os.path.join(base_dir, "config.yml")
            namespaces = []
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = yaml.safe_load(f)
                        namespaces = config.get("namespaces", [])
                except Exception:
                    pass

            # 在每个命名空间下查找
            for namespace in namespaces:
                namespace_dir = os.path.join(base_dir, namespace)
                script_path = find_script_in_path(namespace_dir, parts)
                if script_path:
                    return script_path
        else:
            # 直接在base_dir下查找
            script_path = find_script_in_path(base_dir, parts)
            if script_path:
                return script_path

    return ""


def find_script_in_path(base_dir: str, command_parts: list) -> str:
    """
    在指定路径下查找工作流脚本

    Args:
        base_dir: 基础目录
        command_parts: 命令名称拆分的部分

    Returns:
        找到的脚本路径，如果未找到则返回空字符串
    """
    # 构建工作流目录路径
    workflow_dir = os.path.join(base_dir, *command_parts)

    # 检查目录是否存在
    if not os.path.isdir(workflow_dir):
        return ""

    # 查找目录下的Python脚本
    py_files = [f for f in os.listdir(workflow_dir) if f.endswith(".py")]

    # 如果只有一个Python脚本，直接返回
    if len(py_files) == 1:
        return os.path.join(workflow_dir, py_files[0])

    # 如果有多个Python脚本，查找command.yml
    yml_path = os.path.join(workflow_dir, "command.yml")
    if os.path.exists(yml_path):
        try:
            with open(yml_path, "r", encoding="utf-8") as f:
                yml_content = f.read()

                # 查找steps部分中的脚本名称
                for py_file in py_files:
                    py_file_name = os.path.splitext(py_file)[0]
                    # 查找类似 $command_path/script_name.py 的模式
                    if re.search(rf"\$command_path/{py_file_name}\.py", yml_content):
                        return os.path.join(workflow_dir, py_file)
        except Exception:
            pass

    # 尝试查找与最后一个命令部分同名的脚本
    last_part_script = f"{command_parts[-1]}.py"
    if last_part_script in py_files:
        return os.path.join(workflow_dir, last_part_script)

    # 尝试查找名为command.py的脚本
    if "command.py" in py_files:
        return os.path.join(workflow_dir, "command.py")

    # 没有找到合适的脚本
    return ""


def workflow_call(command: str) -> int:
    """
    调用工作流命令

    Args:
        command: 完整的工作流命令，如 "/github.commit message"

    Returns:
        命令执行的返回码
    """
    # 解析命令和参数
    parts = command.strip().split(maxsplit=1)
    cmd_name = parts[0].lstrip("/")
    cmd_args = parts[1] if len(parts) > 1 else ""

    # 查找对应的工作流脚本
    script_path = find_workflow_script(cmd_name)

    if not script_path:
        print(f"找不到工作流命令: {cmd_name}")
        return 1

    # 使用Popen并将标准输入输出错误流连接到父进程
    process = subprocess.Popen(
        [sys.executable, script_path, cmd_args],
        stdin=sys.stdin,  # 父进程的标准输入传递给子进程
        stdout=sys.stdout,  # 子进程的标准输出传递给父进程
        stderr=sys.stderr,  # 子进程的标准错误传递给父进程
        text=True,  # 使用文本模式
        bufsize=1,  # 行缓冲，确保输出及时显示
    )

    # 等待子进程完成并获取返回码
    return_code = process.wait()

    if return_code != 0:
        print(f"命令执行失败，返回码: {return_code}")

    return return_code


def print_sub_workflows():
    base_dir = os.path.dirname(os.path.abspath(__main__.__file__))
    root_dir = base_dir.split("/")[-1]
    print(f"#### {root_dir.capitalize()} Workflows\n", flush=True)

    for root, dirs, files in os.walk(base_dir):
        if "command.yml" in files:
            if root == base_dir:
                continue
            rel_path = os.path.relpath(root, base_dir)
            workflow_name = f"/{root_dir}.{rel_path.replace(os.path.sep, '.')}"
            if workflow_name.endswith(".zh"):
                continue
            with open(os.path.join(root, "command.yml"), "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                description = config.get("description", "No description available")
                print(f"- **{workflow_name}**: {description}", flush=True)
