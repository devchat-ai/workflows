"""
为workflow命令提供上下文信息

编写工作流实现代码需要的上下文：
1. IDE Service接口定义
2. ChatMark接口定义；
3. 工作流命令列表；
4. 工作流命令组织、实现规范；
5. 基础可用的函数信息；
"""

import os
from typing import List

def load_file_in_user_scripts(filename: str) -> str:
    """
    从用户脚本目录中加载文件内容
    """
    user_path = os.path.expanduser("~/.chat/scripts")
    file_path = os.path.join(user_path, filename)
    with open(file_path, "r") as f:
        return f.read()
    
def load_local_file(filename: str) -> str:
    """
    从当前脚本所在目录的相对目录加载文件内容
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    with open(file_path, "r") as f:
        return f.read()

def load_existing_workflow_defines() -> str:
    """ 从user scripts目录遍历找到所有command.yml文件，并加载其内容 """
    merico_path = os.path.expanduser("~/.chat/scripts/merico")
    community_path = os.path.expanduser("~/.chat/scripts/community")
    custom_path = os.path.expanduser("~/.chat/scripts/custom")

    root_paths = [merico_path]
    # 遍历community_path、custom_path下直接子目录，将其添加到root_paths作为下一步的根目录
    for path in [community_path, custom_path]:
        for root, dirs, files in os.walk(path):
            if root == path:
                root_paths.extend([os.path.join(root, d) for d in dirs])
                break
    
    wrkflow_defines = []
    # 遍历所有根目录，对每个根目录进行递归遍历，找到所有command.yml文件，并加载其内容
    # 将目录名称与command.yml内容拼接成一个字符串，添加到wrkflow_defines列表中
    # 例如：~/.chat/scripts/merico/github/commit/command.yml被找到，那么拼接的字符串为：
    # 工作流命令/github.commit的定义：\n<command.yml内容>\n\n
    for root_path in root_paths:
        for root, dirs, files in os.walk(root_path):
            if "command.yml" in files:
                with open(os.path.join(root, "command.yml"), "r") as f:
                    wrkflow_defines.append(f"工作流命令/{root[len(root_path)+1:].replace(os.sep, '.')}的定义：\n{f.read()}\n\n")
    return "\n".join(wrkflow_defines)


CONTEXTS = f"""
工作流开发需要的上下文信息：


# IDE Service接口定义及使用示例
IDE Service用于在工作流命令中访问与IDE相关的数据，以及调用IDE提供的功能。
## IDEService接口定义
接口定义：
{load_file_in_user_scripts("lib/ide_service/service.py")}
涉及类型定义：
{load_file_in_user_scripts("lib/ide_service/types.py")}

## IDEService接口示例
{load_local_file("ide_service_demo.py")}


# ChatMark接口使用示例
ChatMark用于在工作流命令中与用户交互，展示信息，获取用户输入。
{load_file_in_user_scripts("lib/chatmark/chatmark_example/main.py")}
ChatMark Form组件类似于HTML表单，用于组合多个组件，获取相关设置结果。


# 工作流命令规范
{load_local_file("workflow_guide.md")}


# 已有工作流命令定义
{load_existing_workflow_defines()}


# 工作流内部函数定义
{load_local_file("base_functions_guide.md")}

"""
