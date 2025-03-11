"""
生成工作流命令实现

步骤1: 根据用户输入的工作流命令定义信息，生成相关工作流实现步骤描述，展示相关信息，等待用户确认；
步骤2: 根据用户确认的工作流实现步骤描述，生成工作流命令实现代码，并保存到指定文件中；
"""

#!/usr/bin/env python3
import os
import subprocess
import sys

import yaml
from devchat.llm import chat, chat_json

from lib.chatmark import Form, Radio, Step, TextEditor
from lib.ide_service import IDEService

ROOT_WORKFLOW_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_WORKFLOW_DIR)

from chatflow.util.contexts import CONTEXTS  # noqa: E402

# 工作流命令定义模板
COMMAND_YML_TEMPLATE = """description: {description}
{input_section}
{help_section}{workflow_python_section}
steps:
  - run: ${python_cmd} $command_path/command.py{input_param}
"""

# 工作流命令实现模板
COMMAND_PY_TEMPLATE = """#!/usr/bin/env python3
import os
import sys
from pathlib import Path
{imports}

def main():
    {main_code}

if __name__ == "__main__":
    main()
"""

# 从用户输入提取工作流信息的提示
EXTRACT_INFO_PROMPT = """
请从以下用户输入中提取创建工作流命令所需的关键信息：

用户输入:
{user_input}

工作流上下文信息:
{contexts}

请提取以下信息并以JSON格式返回：
1. command_name: 工作流命令名称，应以/开头，如"/example"或"/category.command"
2. description: 工作流命令的简短描述
3. input_required: 工作流是否需要输入参数(true/false)
4. custom_env: 是否需要自定义Python环境(true/false)
5. env_name: 如果需要自定义环境，环境名称是什么
6. dependencies: 如果需要自定义环境，依赖文件名是什么(如requirements.txt)
7. purpose: 工作流的主要目的和功能
8. implementation_ideas: 实现思路的简要描述

如果某项信息在用户输入中未明确指定，请根据上下文合理推断。

返回格式示例:
{{
  "command_name": "/example.command",
  "description": "这是一个示例命令",
  "input_required": true,
  "custom_env": false,
  "env_name": "",
  "dependencies": "",
  "purpose": "这个命令的主要目的是...",
  "implementation_ideas": "可以通过以下步骤实现..."
}}
"""

# 工作流步骤生成提示
WORKFLOW_STEPS_PROMPT = """
请为以下工作流命令对应脚本文件生成详细的实现步骤描述：

工作流命令名称: {command_name}
工作流命令描述: {description}
输入要求: {input_requirement}
工作流目的: {purpose}
实现思路: {implementation_ideas}

工作流上下文信息:
{contexts}

请提供清晰的步骤描述，包括：
1. 每个步骤需要完成的具体任务
2. 每个步骤可能需要的输入和输出
3. 每个步骤可能需要使用的IDE Service或ChatMark组件
4. 任何其他实现细节

返回格式应为markdown块包裹的步骤列表，每个步骤都有详细描述。输出示例如下：
```steps
步骤1: 获取用户输入的重构任务要求
步骤2: 调用IDE Service获取选中代码
步骤3: 根据用户重构任务要求，调用大模型生成选中代码的重构代码
步骤4: 调用IDE Service，将生成的重构代码通过DIFF VIEW方式展示给用户
```

不要输出工作流命令的其他构建步骤，只需要清洗描述工作流命令对应command.py中对应的步骤实现即可。
"""

# 代码实现生成提示
CODE_IMPLEMENTATION_PROMPT = """
请为以下工作流命令生成Python实现代码：

工作流命令名称: {command_name}
工作流命令描述: {description}
输入要求: {input_requirement}
自定义环境: {custom_env}
工作流实现步骤:
{workflow_steps}

工作流上下文信息:
{contexts}

请生成完整的Python代码实现，包括：
1. 必要的导入语句
2. 主函数实现
3. 按照工作流步骤实现具体功能
4. 适当的错误处理
5. 必要的注释说明
6. 所有markdown代码块都要有明确的语言标识，如python、json、yaml、code等

代码应该使用IDE Service接口与IDE交互，使用ChatMark组件与用户交互。
输出格式应为markdown代码块，语言标识为python。仅输出工作流实现对应的脚本代码块，不需要输出其他逻辑信息。

只需要输出最终PYTHON代码块，不需要其他信息。例如：
```python
....
```
"""


@chat_json(prompt=EXTRACT_INFO_PROMPT)
def extract_workflow_info(user_input, contexts):
    """从用户输入中提取工作流信息"""
    pass


@chat(prompt=WORKFLOW_STEPS_PROMPT, stream_out=False)
def generate_workflow_steps(
    command_name, description, input_requirement, purpose, implementation_ideas, contexts
):
    """生成工作流实现步骤描述"""
    pass


@chat(prompt=CODE_IMPLEMENTATION_PROMPT, stream_out=False)
def generate_workflow_code(
    command_name, description, input_requirement, custom_env, workflow_steps, contexts
):
    """生成工作流实现代码"""
    pass


def parse_command_path(command_name):
    """
    解析命令路径，返回目录结构和最终命令名
    确保工作流创建在custom目录下的有效namespace中
    """
    parts = command_name.strip("/").split(".")

    # 获取custom目录路径
    custom_dir = os.path.join(os.path.expanduser("~"), ".chat", "scripts", "custom")

    # 获取custom目录下的有效namespace
    valid_namespaces = []
    config_path = os.path.join(custom_dir, "config.yml")

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                if config and "namespaces" in config:
                    valid_namespaces = config["namespaces"]
        except Exception as e:
            print(f"读取custom配置文件失败: {str(e)}")

    # 如果没有找到有效namespace，使用默认namespace
    if not valid_namespaces:
        print("警告: 未找到有效的custom namespace，将使用默认namespace 'default'")
        valid_namespaces = ["default"]

        # 确保default namespace存在于config.yml中
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w") as f:
                yaml.dump({"namespaces": ["default"]}, f)
        except Exception as e:
            print(f"创建默认namespace配置失败: {str(e)}")

    # 使用第一个有效namespace
    namespace = valid_namespaces[0]

    # 创建最终命令目录路径
    command_dir = os.path.join(custom_dir, namespace)

    # 创建目录结构
    for part in parts[:-1]:
        command_dir = os.path.join(command_dir, part)

    return command_dir, parts[-1]


def parse_markdown_block(response, block_type="steps"):
    """
    从AI响应中解析指定类型的Markdown代码块内容，支持处理嵌套的代码块。

    Args:
        response (str): AI生成的响应文本
        block_type (str): 要解析的代码块类型，默认为"steps"

    Returns:
        str: 解析出的代码块内容

    Raises:
        Exception: 解析失败时抛出异常
    """
    try:
        # 处理可能存在的思考过程
        if response.find("</think>") != -1:
            response = response.split("</think>")[-1]

        # 构建起始标记
        start_marker = f"```{block_type}"
        end_marker = "```"

        # 查找起始位置
        start_pos = response.find(start_marker)
        if start_pos == -1:
            # 如果没有找到指定类型的标记，直接返回原文本
            return response.strip()

        # 从标记后开始的位置
        content_start = start_pos + len(start_marker)

        # 从content_start开始找到第一个未配对的```
        pos = content_start
        open_blocks = 1  # 已经有一个开放的块

        while True:
            # 找到下一个```
            next_marker = response.find(end_marker, pos)
            if next_marker == -1:
                # 如果没有找到结束标记，返回剩余所有内容
                break

            # 检查这是开始还是结束标记
            # 向后看是否跟着语言标识符
            after_marker = response[next_marker + 3 :]
            # 检查是否是新的代码块开始 - 只要```后面跟着非空白字符，就认为是新代码块开始
            if after_marker.strip() and not after_marker.startswith("\n"):
                first_word = after_marker.split()[0]
                if not any(c in first_word for c in ",.;:!?()[]{}"):
                    open_blocks += 1
                else:
                    open_blocks -= 1
            else:
                open_blocks -= 1

            if open_blocks == 0:
                # 找到匹配的结束标记
                return response[content_start:next_marker].strip()

            pos = next_marker + 3

        # 如果没有找到匹配的结束标记，返回从content_start到末尾的内容
        return response[content_start:].strip()

    except Exception as e:
        import logging

        logging.info(f"Response: {response}")
        logging.error(f"Exception in parse_markdown_block: {str(e)}")
        raise Exception(f"解析{block_type}内容失败: {str(e)}") from e


def create_workflow_files(command_dir, command_name, description, input_required, code):
    """创建工作流命令文件"""
    # 创建命令目录
    os.makedirs(command_dir, exist_ok=True)

    # 创建command.yml
    input_section = f"input: {'required' if input_required else 'optional'}"
    help_section = "help: README.md"
    input_param = ' "$input"' if input_required else ""

    # 添加自定义环境配置
    workflow_python_section = ""
    python_cmd = "devchat_python"

    yml_content = COMMAND_YML_TEMPLATE.format(
        description=description,
        input_section=input_section,
        help_section=help_section,
        workflow_python_section=workflow_python_section,
        python_cmd=python_cmd,
        input_param=input_param,
    )

    with open(os.path.join(command_dir, "command.yml"), "w") as f:
        f.write(yml_content)

    # 创建command.py
    with open(os.path.join(command_dir, "command.py"), "w") as f:
        f.write(code)

    # 设置执行权限
    os.chmod(os.path.join(command_dir, "command.py"), 0o755)

    # 创建README.md
    readme_content = f"# {command_name}\n\n{description}\n"
    with open(os.path.join(command_dir, "README.md"), "w") as f:
        f.write(readme_content)


def main():
    # 获取用户输入
    user_input = sys.argv[1] if len(sys.argv) > 1 else ""

    # 步骤1: 通过AI分析用户输入，提取必要信息
    with Step("分析用户输入，提取工作流信息..."):
        workflow_info = extract_workflow_info(user_input=user_input, contexts=CONTEXTS)

    # 步骤3: 生成工作流实现步骤描述
    with Step("生成工作流实现步骤描述..."):
        workflow_steps = generate_workflow_steps(
            command_name=workflow_info.get("command_name", ""),
            description=workflow_info.get("description", ""),
            input_requirement="可选",
            purpose=workflow_info.get("purpose", ""),
            implementation_ideas=workflow_info.get("implementation_ideas", ""),
            contexts=CONTEXTS,
        )

    workflow_steps = parse_markdown_block(workflow_steps, block_type="steps")

    # 步骤2: 使用Form组件一次性展示所有信息，让用户编辑
    print("\n## 工作流信息\n")

    # 创建所有编辑组件
    command_name_editor = TextEditor(workflow_info.get("command_name", "/example.command"))
    description_editor = TextEditor(workflow_info.get("description", "工作流命令描述"))
    input_radio = Radio(["必选 (required)", "可选 (optional)"])
    purpose_editor = TextEditor(workflow_info.get("purpose", "请描述工作流的主要目的和功能"))
    # ideas_editor = TextEditor(workflow_info.get("implementation_ideas", "请描述实现思路"))
    steps_editor = TextEditor(workflow_steps)

    # 使用Form组件一次性展示所有编辑组件
    form = Form(
        [
            "命令名称:",
            command_name_editor,
            "输入要求:",
            input_radio,
            "描述:",
            description_editor,
            "工作流目的:",
            purpose_editor,
            "实现步骤:",
            steps_editor,
        ]
    )

    form.render()

    # 获取用户编辑后的值
    command_name = command_name_editor.new_text
    description = description_editor.new_text
    input_required = input_radio.selection == 0
    # implementation_ideas = ideas_editor.new_text
    workflow_steps = steps_editor.new_text

    # 步骤4: 生成工作流实现代码
    with Step("生成工作流实现代码..."):
        code = generate_workflow_code(
            command_name=command_name,
            description=description,
            input_requirement="必选" if input_required else "可选",
            custom_env=False,
            workflow_steps=workflow_steps,
            contexts=CONTEXTS,
        )

    code = code.strip()
    start_index = code.find("```python")
    end_index = code.rfind("```")
    code = code[start_index + len("```python") : end_index].strip()
    # code = parse_markdown_block(code, block_type="python")

    # 解析命令路径
    command_dir, final_command = parse_command_path(command_name)
    full_command_dir = os.path.join(command_dir, final_command)

    # 步骤5: 创建工作流文件
    with Step(f"创建工作流文件到 {full_command_dir}"):
        create_workflow_files(full_command_dir, command_name, description, input_required, code)

    # 更新斜杠命令
    with Step("更新斜杠命令..."):
        IDEService().update_slash_commands()

    # 在新窗口中打开工作流目录
    try:
        subprocess.run(["code", full_command_dir], check=True)
    except subprocess.SubprocessError:
        print(f"无法自动打开编辑器，请手动打开工作流目录: {full_command_dir}")

    print(f"\n✅ 工作流命令 {command_name} 已成功创建！")
    print(f"命令文件位置: {full_command_dir}")
    print("你现在可以在DevChat中使用这个命令了。")


if __name__ == "__main__":
    main()
