#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import Dict

from devchat.llm import chat_json

from lib.chatmark import Button, Form, TextEditor
from lib.ide_service import IDEService
from lib.workflow import workflow_call

# 步骤3: 使用AI识别API路径和METHOD的提示词
API_ANALYSIS_PROMPT = """
分析以下代码，识别其中的API路径和HTTP方法。

代码:
```
{code}
```

请提取代码中定义或使用的API路径和HTTP方法(GET, POST, PUT, DELETE等)。
如果代码中有多个API，请识别最主要的一个。
如果无法确定HTTP方法，请使用"GET"作为默认值。

返回JSON格式如下:
{{
  "api_path": "识别到的API路径，例如/api/users",
  "method": "识别到的HTTP方法，例如GET、POST、PUT、DELETE等"
}}
"""


@chat_json(prompt=API_ANALYSIS_PROMPT)
def analyze_api(code: str) -> Dict[str, str]:
    """使用AI分析代码中的API路径和HTTP方法"""
    pass


def main() -> None:
    """API重构工作流主函数"""
    try:
        # 步骤1: 获取用户输入的重构目标
        if len(sys.argv) < 2:
            print("错误: 请提供重构目标")
            sys.exit(1)

        refactor_target = sys.argv[1]

        # 步骤2: 获取用户选中的代码
        selected_code = IDEService().get_selected_range()
        if not selected_code or not selected_code.text.strip():
            print("错误: 请先选择需要重构的代码")
            sys.exit(1)

        # 步骤3: 使用AI识别API路径和METHOD
        print("正在分析选中代码中的API信息...")
        api_info = analyze_api(code=selected_code.text)

        if not api_info or "api_path" not in api_info or "method" not in api_info:
            print("错误: 无法识别API信息")
            sys.exit(1)

        api_path = api_info["api_path"]
        method = api_info["method"]

        # 步骤4: 显示识别结果并让用户确认
        print("识别到的API信息:")
        print(f"API路径: {api_path}")
        print(f"HTTP方法: {method}")

        api_path_editor = TextEditor(api_path)

        form = Form(
            [
                "### 请确认API信息",
                "API路径:",
                api_path_editor,
                f"HTTP方法: {method}",
                "请确认或修改API路径，然后点击下方按钮继续",
            ]
        )

        form.render()

        # 获取用户确认后的API路径
        confirmed_api_path = api_path_editor.new_text

        # 步骤5: 调用重构工作流进行代码重构
        print(f"正在重构API: {confirmed_api_path}...")
        refactor_result = workflow_call(f"/refactor {refactor_target}")

        if refactor_result != 0:
            print("错误: API重构失败")
            sys.exit(1)

        print("API重构成功!")

        # 步骤6: 显示按钮让用户确认是否继续
        continue_button = Button(["提交修改并测试API", "结束重构"])
        continue_button.render()

        if continue_button.clicked == 1:  # 用户选择结束
            print("API重构已完成，未提交修改")
            return

        # 步骤7: 调用GitHub提交工作流提交修改
        print("正在提交修改...")
        commit_result = workflow_call("/github.commit")

        if commit_result != 0:
            print("警告: 代码提交失败，但将继续进行API测试")
        else:
            print("代码提交成功!")

        # 步骤8: 调用API测试工作流对重构API进行测试
        print("正在准备API测试...")
        test_command = f"/test.api.upload {confirmed_api_path} {method} {refactor_target}"
        test_result = workflow_call(test_command)

        if test_result != 0:
            print("警告: API测试可能未成功完成")

        print("API重构工作流执行完毕!")

    except Exception as e:
        print(f"错误: 执行过程中发生异常: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
