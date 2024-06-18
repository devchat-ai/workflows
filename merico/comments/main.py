import os
import re
import sys

from devchat.llm import chat
from devchat.memory import FixSizeChatMemory

from lib.ide_service import IDEService

PROMPT = """
file: {file_path}
```
{selected_text}
```
"""

PROMPT_ZH = """
文件：{file_path}
```
{selected_text}
```
代码块中注释请使用中文描述。
"""


MESSAGES_FEW_SHOT = [
    {
        "role": "system",
        "content": """
You are a code assistant. Your task is to add comments for given code block.
To add comments, you need to follow the following rules:
1. don't change any code in code block, even space char;
2. comment should be placed before the code line, don't append comment to the code line;
3. keep comments already in code block;
4. add comments for each code line;
5. don't change string value in code block;

there are a examples with correct outputs:
input:
file: a1.py
```
# print("hello")

print("Hello World") print("Hello World2")
```
output:
```python
# print("hello")

# print Hello World
print("Hello World") print("Hello World2")
```
In this example, "# print("hello")" is comment line, but we keep it in output.
"print("Hello World") print("Hello World2")" is an error line, but we keep it in output,
because output can't change any code, just insert comment lines to code block.


here is an error example:
```
        // const filepath = document.uri.fsPath;
        // const fileContent = document.getText();
        // const posOffset = document.offsetAt(position);
        // await outputAst(filepath, fileContent, posOffset);
        // // await testTreesitterQuery(filepath, fileContent);
        // logger.channel()?.info("Result:", result2);
        // if (1) {
        //     return [];
        // }

        let response: CodeCompleteResult | undefined = undefined;
```
output is :
```typescript
        // init response
        let response: CodeCompleteResult | undefined = undefined;
```
In this example, comments lines are missed, so this output is bad.

here is an error example:
```
    const value = "open file";
```
output is :
```typescript
    // 设置变量值为打开文件
    const value = "打开文件";
```
In this example, string in code is changed, so this output is bad.

Output should format as code block.
""",
    },
    {
        "role": "user",
        "content": """
file: a1.py
```
    print("hello")
```
""",
    },
    {
        "role": "assistant",
        "content": """
```python
    # print hello
    print("hello")
```
""",
    },
    {
        "role": "user",
        "content": """
file: a1.py
```
    print("hell\\nworld")
```
""",
    },
    {
        "role": "assistant",
        "content": """
```python
    # print hello world
    print("hell\\nworld")
```
""",
    },
    {
        "role": "user",
        "content": """
file: t2.ts
```
                this.logEventToServer(
                {
                    completion_id: response!.id,
                    type: "select",
                    lines: response!.code.split('\\n').length,
                    length: response!.code.length
                });
```
""",
    },
    {
        "role": "assistant",
        "content": """
```typescript
                // log event to server
                this.logEventToServer(
                {
                    // completion id
                    completion_id: response!.id,
                    // type of event
                    type: "select",
                    // number of lines in response code
                    lines: response!.code.split('\\n').length,
                    // length of response code
                    length: response!.code.length
                });
```
""",
    },
    {
        "role": "user",
        "content": """
file: t2.ts
```
    // if (a == 1) {
    //     console.log("a is 1");
    // }

    if (a == 2) {
        console.log("a is 2");
    }
```
""",
    },
    {
        "role": "assistant",
        "content": """
```typescript
    // if (a == 1) {
    //     console.log("a is 1");
    // }

    // check if a is 2
    if (a == 2) {
        // log a is 2
        console.log("a is 2");
    }
```
""",
    },
]


def get_selected_code():
    """Retrieves the selected lines of code from the user's selection."""
    selected_data = IDEService().get_selected_range().dict()
    if selected_data["range"]["start"] == selected_data["range"]["end"]:
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_text = f.read()
                print(readme_text)
                sys.exit(0)
        print("Please select some text.", file=sys.stderr, flush=True)
        sys.exit(-1)
    return selected_data


memory = FixSizeChatMemory(max_size=20, messages=MESSAGES_FEW_SHOT)


def get_prompt():
    ide_language = IDEService().ide_language()
    return PROMPT_ZH if ide_language == "zh" else PROMPT


@chat(prompt=get_prompt(), stream_out=True, memory=memory)
# pylint: disable=unused-argument
def add_comments(selected_text, file_path):
    """Call AI to rewrite selected code"""
    pass  # pylint: disable=unnecessary-pass


def extract_markdown_block(text):
    """Extracts the first Markdown code block from the given text without the language specifier."""
    pattern = r"```(?:\w+)?\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        block_content = match.group(1)
        return block_content
    else:
        if text.find("```"):
            return None
        return text


def remove_unnecessary_escapes(code_a, code_b):
    code_copy = code_b  # Create a copy of the original code
    escape_chars = re.finditer(r"\\(.)", code_b)
    remove_char_index = []
    for match in escape_chars:
        before = code_b[max(0, match.start() - 4) : match.start()]
        after = code_b[match.start() + 1 : match.start() + 5]
        substr = before + after
        if substr in code_a:
            remove_char_index.append(match.start())
    remove_char_index.reverse()
    for index in remove_char_index:
        code_copy = code_copy[:index] + code_copy[index + 1 :]
    return code_copy


def main():
    selected_text = get_selected_code()
    file_path = selected_text.get("abspath", "")
    code_text = selected_text.get("text", "")

    response = add_comments(selected_text=code_text, file_path=file_path)
    if not response:
        sys.exit(1)
    new_code = extract_markdown_block(response)

    if not new_code:
        ide_lang = IDEService().ide_language()
        error_msg = (
            "\n\nThe output of the LLM is incomplete and cannot perform code operations.\n\n"
            if ide_lang != "zh"
            else "\n\n大模型输出不完整，不能进行代码操作。\n\n"
        )
        print(error_msg)
        sys.exit(0)

    new_code = remove_unnecessary_escapes(code_text, new_code)
    IDEService().diff_apply("", new_code)
    sys.exit(0)


if __name__ == "__main__":
    main()
