import os
import re
import sys

from typing import List, Dict, Any, Optional, Tuple

from devchat.llm import chat, chat_json

from lib.ide_service import IDEService
from lib.chatmark import Step, Form, TextEditor


def get_selected_code():
    """
    Retrieves the selected lines of code from the user's selection.

    This function extracts the text selected by the user in their IDE or text editor.
    If no text has been selected, it prints an error message to stderr and exits the
    program with a non-zero status indicating failure.

    Returns:
        dict: A dictionary containing the key 'selectedText' with the selected text
        as its value. If no text is selected, the program exits.
    """
    selected_data = IDEService().get_selected_range().dict()

    miss_selected_error = "Please select some text."
    if selected_data["range"]["start"] == selected_data["range"]["end"]:
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_text = f.read()
                print(readme_text)
                sys.exit(0)

        print(miss_selected_error, file=sys.stderr, flush=True)
        sys.exit(-1)

    return selected_data


REWRITE_PROMPT = prompt = """
你是一个代码重构专家，你的任务是根据用户的需求重写代码。你需要根据用户的需求，重写代码，并保证代码的语法正确性和逻辑正确性。
你的重构目标：
{question}

待重构的代码：
{selected_text}

项目中其他相关上下文代码：
{context_code}

围绕重构目标对代码进行重构，不要进行重构目标之外的其他代码优化修改。
输出重构后的代码，代码需要用markdown代码块包裹,代码需要与原重构代码保持同样的缩进格式，并且代码块的语言类型需要与原重构代码保持一致，例如：
```python
...
```
以及
```java
...
```

只输出最终重构后代码，不要输出其他任何内容。
"""


@chat(prompt=REWRITE_PROMPT, stream_out=True)
# pylint: disable=unused-argument
def ai_rewrite(question, selected_text, context_code):
    """
    call ai to rewrite selected code
    """
    pass  # pylint: disable=unnecessary-pass


def extract_markdown_block(text):
    """
    Extracts the first Markdown code block from the given text without the language specifier.

    :param text: A string containing Markdown text
    :return: The content of the first Markdown code block, or None if not found
    """
    pattern = r"```(?:\w+)?\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        block_content = match.group(1)
        return block_content
    else:
        # whether exist ```language?
        if text.find("```"):
            return None
        return text


def replace_selected(new_code):
    selected_data = IDEService().get_selected_code().dict()
    select_file = selected_data["abspath"]
    select_range = selected_data["range"]  # [start_line, start_col, end_line, end_col]

    # Read the file
    with open(select_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    lines.append("\n")

    # Modify the selected lines
    start_line = select_range["start"]["line"]
    start_col = select_range["start"]["character"]
    end_line = select_range["end"]["line"]
    end_col = select_range["end"]["character"]

    # If the selection spans multiple lines, handle the last line and delete the lines in between
    if start_line != end_line:
        lines[start_line] = lines[start_line][:start_col] + new_code
        # Append the text after the selection on the last line
        lines[start_line] += lines[end_line][end_col:]
        # Delete the lines between start_line and end_line
        del lines[start_line + 1 : end_line + 1]
    else:
        # If the selection is within a single line, remove the selected text
        lines[start_line] = lines[start_line][:start_col] + new_code + lines[end_line][end_col:]

    # Combine everything back together
    modified_text = "".join(lines)

    # Write the changes back to the file
    with open(select_file, "w", encoding="utf-8") as file:
        file.write(modified_text)





# 定义用于分析代码中缺少定义的符号的提示
SYMBOL_ANALYSIS_PROMPT = """
角色：你是一个资深的程序工程师，擅长代码分析与代码重构。

重构目标：
{task}

当前用户选择代码片段：
{code}

你的任务：
针对当前已知代码，找出所有可能缺少定义的符号（变量、函数、类等）。这些符号在代码中被使用，但可能没有在当前上下文中定义。

输出要求，输出markdown代码块形式的JSON块，形式为：
```json
[
    {{
        "symbol": "<identifier>",
        "line": "<identifier所在行完整代码，包含缩进空格>",
        "value": "<影响重要度0-1之间>",
        "reason": "<影响描述>"
    }},
    ......
]
```

示例：
针对以下代码片段：
```python
def fun1():
    fun2("hello")
    fun3(
        "hello"
    )
```
进行重构，希望fun1执行打印输出hello DevChat。

此时由于缺少fun2,fun3的函数定义，所以并不清楚fun1的完整执行逻辑。所以输出：
```json
[
    {{
        "symbol": "fun2",
        "line": "    fun2(\"hello\")",
        "value": 0.8,
        "reason": "不能确定fun2中具体代码逻辑，是否会打印输出参数'hello'，如果是，那么重构只需要修改fun1中参数信息"
    }},
    {{
        "symbol": "fun3",
        "line": "    fun3(",
        "value": 0.8,
        "reason": "不能确定fun3中具体代码逻辑，是否会打印输出参数'hello'，如果是，那么重构只需要修改fun1中参数信息"
    }}
]
```

请确保返回的JSON格式正确，只包含实际缺少定义的符号。只输出最终结果JSON，不要输出其他解释描述。
"""

# 定义用于生成符号使用建议的提示
SYMBOL_USAGE_PROMPT = """
基于以下符号的定义，生成正确使用这些符号的建议。

符号定义:
{symbol_definitions}

原始代码片段:
```
{original_code}
```

请提供以下内容：
1. 对每个符号的正确使用方法的解释
2. 在原始代码中可能存在的符号使用错误
3. 修复建议
4. 示例代码，展示如何正确使用这些符号

请以JSON格式返回，包含以下字段：
1. "suggestions": 包含所有符号使用建议的数组，每个建议包含：
   - "symbol": 符号名称
   - "explanation": 符号的正确使用方法解释
   - "errors": 在原始代码中可能存在的使用错误
   - "fix": 修复建议
   - "example": 示例代码

请确保返回的JSON格式正确。
"""

@chat_json(prompt=SYMBOL_ANALYSIS_PROMPT)
def analyze_missing_symbols(code: str, task: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    使用大模型分析代码片段中缺少定义的符号
    
    Args:
        code: 需要分析的代码片段
        
    Returns:
        包含缺少定义的符号列表的字典
    """
    pass

@chat_json(prompt=SYMBOL_USAGE_PROMPT)
def generate_symbol_usage_suggestions(symbol_definitions: str, original_code: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    基于符号定义生成符号使用建议
    
    Args:
        symbol_definitions: 符号定义的文本表示
        original_code: 原始代码片段
        
    Returns:
        包含符号使用建议的字典
    """
    pass

def get_symbol_definition(abspath: str, line: int, character: int, symbol_name: str, symbol_type: str, project_root_path: str) -> List[Tuple]:
    """
    获取符号定义的代码
    
    Args:
        abspath: 文件的绝对路径
        line: 符号所在行
        character: 符号所在列
        symbol_type: 符号类型
        
    Returns:
        符号定义的代码，如果找不到则返回None
    """
    ide_service = IDEService()
    locations = []
    has_visited = set()
    
    # 根据符号类型选择合适的查找方法
    locations1 = ide_service.find_type_def_locations(abspath, line, character)
    locations2 = ide_service.find_def_locations(abspath, line, character)
    locations3 = ide_service.find_type_def_locations(abspath, line, character + len(symbol_name) - 1)
    locations4 = ide_service.find_def_locations(abspath, line, character + len(symbol_name) - 1)
    for location in locations1 + locations2 + locations3 + locations4:
        if not location.abspath.startswith(project_root_path):
            continue
        key = (location.abspath, location.range.start.line, location.range.end.line)
        key_str = f"{location.abspath}:{location.range.start.line}:{location.range.end.line}"
        if key_str not in has_visited:
            has_visited.add(key_str)
            locations.append(key)

    return locations


def format_symbol_results(symbols: List[Dict[str, Any]], definitions: Dict[str, str]) -> str:
    """
    格式化符号分析结果为Markdown格式
    
    Args:
        symbols: 符号列表
        definitions: 符号定义字典
        
    Returns:
        格式化后的Markdown文本
    """
    result = "## 符号分析结果\n\n"
    
    if not symbols:
        return result + "没有找到缺少定义的符号。"
    
    result += f"找到 {len(symbols)} 个可能缺少定义的符号：\n\n"
    
    for i, symbol in enumerate(symbols):
        result += f"### {i+1}. {symbol['name']} ({symbol['type']})\n\n"
        result += f"- 位置: 第{symbol['line'] + 1}行，第{symbol['character'] + 1}列\n"
        result += f"- 原因: {symbol['reason']}\n\n"
        
        if symbol['name'] in definitions and definitions[symbol['name']]:
            result += "#### 找到的定义:\n\n"
            result += f"{definitions[symbol['name']]}\n\n"
        else:
            result += "#### 未找到定义\n\n"
            result += "无法在当前项目中找到此符号的定义。可能是外部库、内置函数或拼写错误。\n\n"
    
    return result

def format_usage_suggestions(suggestions: List[Dict[str, Any]]) -> str:
    """
    格式化符号使用建议为Markdown格式
    
    Args:
        suggestions: 符号使用建议列表
        
    Returns:
        格式化后的Markdown文本
    """
    if not suggestions:
        return ""
    
    result = "## 符号使用建议\n\n"
    
    for i, suggestion in enumerate(suggestions):
        result += f"### {i+1}. {suggestion['symbol']}\n\n"
        result += f"**正确使用方法**:\n{suggestion['explanation']}\n\n"
        
        if suggestion.get('errors'):
            result += f"**可能存在的错误**:\n{suggestion['errors']}\n\n"
        
        if suggestion.get('fix'):
            result += f"**修复建议**:\n{suggestion['fix']}\n\n"
        
        if suggestion.get('example'):
            result += "**示例代码**:\n```python\n" + suggestion['example'] + "\n```\n\n"
    
    return result


def find_project_root(file_path: str) -> str:
    """
    根据文件路径查找项目根目录
    
    通过向上遍历目录，查找 .git 或 .svn 目录来确定项目根目录
    
    Args:
        file_path: 文件的绝对路径
        
    Returns:
        项目根目录的绝对路径，如果找不到则返回原始文件所在目录
    """
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
        
    current_dir = os.path.dirname(file_path)
    
    # 向上遍历目录，直到找到包含 .git 或 .svn 的目录，或者到达根目录
    while current_dir and current_dir != '/':
        # 检查当前目录是否包含 .git 或 .svn
        if os.path.exists(os.path.join(current_dir, '.git')) or \
           os.path.exists(os.path.join(current_dir, '.svn')):
            return current_dir
        
        # 向上移动一级目录
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # 防止在Windows根目录下无限循环
            break
        current_dir = parent_dir
    
    # 如果没有找到版本控制目录，返回文件所在目录
    return os.path.dirname(file_path)


def main():
    ide_service = IDEService()
    question = sys.argv[1]
    rafact_task = sys.argv[1]
    # prepare code


    # 步骤1: 获取用户选中的代码片段
    with Step("获取选中的代码片段..."):
        selected_code = ide_service.get_selected_range()
        
        if not selected_code or not selected_code.text.strip():
            print("请先选择一段代码片段再执行此命令。")
            return
    # print(selected_code)
    selected_text = selected_code.text
    project_root_path = find_project_root(selected_code.abspath)
    print(f"项目根目录: {project_root_path}\n\n")


    # 步骤2: 分析代码片段中缺少定义的符号
    with Step("分析代码中缺少定义的符号..."):
        try:
            analysis_result = analyze_missing_symbols(code=selected_code.text, task=rafact_task)
            missing_symbols = analysis_result  # 直接获取返回的列表
            
            if not missing_symbols:
                print("没有找到缺少定义的符号。")
                return
                
            ide_service.ide_logging("info", f"找到 {len(missing_symbols)} 个可能缺少定义的符号")
        except Exception as e:
            ide_service.ide_logging("error", f"分析符号时出错: {str(e)}")
            print(f"分析代码时出错: {str(e)}")
            return

    current_filepath = selected_code.abspath
    base_line = selected_code.range.start.line
    # range = "abspath='/Users/boboyang/.chat/scripts/merico/symbol_resolver/command.py' range=line=248 character=0 - line=248 character=24 text=' print(selected_code)'"

    # 步骤3: 将分析结果转换为可处理的结构
    with Step("处理符号信息..."):
        symbols = []
        code_lines = selected_code.text.splitlines()
        
        for symbol_info in missing_symbols:
            symbol_name = symbol_info["symbol"]
            symbol_line_text = symbol_info["line"]
            
            # 在代码中查找匹配的行
            line_index = -1
            for i, line in enumerate(code_lines):
                if line == symbol_line_text:
                    line_index = i
                    break
            
            if line_index == -1:
                ide_service.ide_logging("warning", f"找不到符号 {symbol_name} 所在行")
                continue
            
            # 在行中查找符号位置
            char_index = symbol_line_text.find(symbol_name)
            if char_index == -1:
                ide_service.ide_logging("warning", f"在行中找不到符号 {symbol_name}")
                continue
            
            # 构建符号信息
            symbol = {
                "name": symbol_name,
                "line": base_line + line_index,
                "character": char_index,
                "type": "unknown",  # 默认类型
                "reason": symbol_info.get("reason", "未知原因")
            }
            
            symbols.append(symbol)
    
    # 步骤3: 查找符号的实际定义
    with Step("查找符号的实际定义..."):
        symbol_definitions = {}
        
        for symbol in symbols:
            symbol_name = symbol["name"]
            symbol_line = symbol.get("line", 0)
            symbol_char = symbol.get("character", 0)
            symbol_type = symbol.get("type", "unknown")
            
            definitions = get_symbol_definition(
                selected_code.abspath, 
                symbol_line, 
                symbol_char, 
                symbol_name,
                symbol_type,
                project_root_path
            )
            
            symbol_definitions[symbol_name] = definitions
    
    # 计算每个文件被引用次数
    files_ref_counts = {}
    # 当前选中代码文件，默认计算100
    files_ref_counts[selected_code.abspath] = 100
    for symbol in symbol_definitions:
        for definition in symbol_definitions[symbol]:
            if definition[0] not in files_ref_counts:
                files_ref_counts[definition[0]] = 0
            files_ref_counts[definition[0]] += 1

    context_code = ""
    for filepath, ref_count in files_ref_counts.items():
        if ref_count > 0:
            with open(filepath, "r") as f:
                context_code += f"文件名：{filepath}\n\n"
                context_code += "文件内容：\n"
                context_code += f.read()
                context_code += "\n\n"

    # rewrite
    response = ai_rewrite(question=question, selected_text=selected_text, context_code=context_code)
    if not response:
        sys.exit(1)

    # apply new code to editor
    new_code = extract_markdown_block(response)
    if not new_code:
        if IDEService().ide_language() == "zh":
            print("\n\n大模型输出不完整，不能进行代码操作。\n\n")
        else:
            print("\n\nThe output of the LLM is incomplete and cannot perform code operations.\n\n")
        sys.exit(0)

    IDEService().diff_apply("", new_code)

    sys.exit(0)


if __name__ == "__main__":
    main()
