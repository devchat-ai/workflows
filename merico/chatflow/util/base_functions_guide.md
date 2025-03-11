工作流开发中封装了部分基础函数，方便开发者在工作流中使用。

**大模型调用** 
针对大模型调用，封装了几个装饰器函数，分别用于调用大模型生成文本和生成json格式的文本。
- chat装饰器
用于调用大模型生成文本，并将生成的文本返回给调用者。具体使用示例如下：
```python
from devchat.llm import chat

PROMPT = """
对以下代码段进行解释：
{code}
"""
@chat(prompt=PROMPT, stream_out=True)
# pylint: disable=unused-argument
def explain(code):
    """
    call ai to explain selected code
    """
    pass

ai_explanation = explain(code="def foo(): pass")
```
调用explain函数时，需要使用参数名称=参数值的方式传递参数，参数名称必须与PROMPT中使用的参数名称一致。

- chat_json装饰器
用于调用大模型生成json对象。具体使用示例如下：
```python
from devchat.llm import chat_json
PROMPT = (
    "Give me 5 different git branch names, "
    "mainly hoping to express: {task}, "
    "Good branch name should looks like: <type>/<main content>,"
    "the final result is output in JSON format, "
    'as follows: {{"names":["name1", "name2", .. "name5"]}}\n'
)


@chat_json(prompt=PROMPT)
def generate_branch_name(task):
    pass

task = "fix bug"
branch_names = generate_branch_name(task=task)
print(branch_names["names"])
```
调用generate_branch_name函数时，需要使用参数名称=参数值的方式传递参数，参数名称必须与PROMPT中使用的参数名称一致。
使用chat, chat_json的注意：
1. 使用chat_json装饰器时，返回的结果是一个字典对象，在PROMPT中描述这个字典对象的结构时需要使用{{}}来表示{}。因为后续操作中会使用类似f-string的方式替代PROMPT中的参数，所以在PROMPT中使用{}时需要使用{{}}来表示{}。
2. 使用这两个装饰器时，PROMPT中不要使用markdown的代码块语法。

**工作流调用**
目的是对已有工作流进行复用，在A工作流中调用B工作流。
- workflow_call函数
调用指定的工作流，并将指定的参数传递给被调用的工作流。具体使用示例如下：
```python
from lib.workflow import workflow_call

ret_code = workflow_call("/helloworld some name")
if ret_code == 0:
    print("workflow call success")
else:
    print("workflow call failed")
```