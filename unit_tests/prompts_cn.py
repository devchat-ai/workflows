# ruff: noqa: E501
# Don not limit the length of each line of the prompts.


PROPOSE_TEST_PROMPT = """
你是一位智能测试用例生成助手。
给定一个用户提示和一个目标函数，请根据提示为目标函数生成测试用例。

用户提示如下：

{user_prompt}

目标函数是 `{function_name}`， 该函数所在的文件是 {file_path}。

以下是与该函数相关的源代码：

{relevant_content}

请为每个测试用例提供一句话的描述，描述该测试用例所测试的行为。
你不需要用代码编写测试用例，只需用普通的自然语言描述即可。
最多生成 6 个测试用例。

请按照以下JSON格式回复：
{{
    "test_cases": [
        {{"description": "<测试用例1的自然语言描述>"}},
        {{"description": "<测试用例2的自然语言描述>"}},
    ]
}}
"""


FIND_REFERENCE_PROMPT = """
请找到一个合适的参考测试文件，该文件可用于为文件 {file_path} 中的 `{function_name}` 函数编写测试提供指导。
参考文件应该提供一个清晰的示例，演示测试类似性质的函数的最佳实践。
"""


WRITE_TESTS_PROMPT = """
你是一位智能单元测试生成助手。
给定一个目标函数、一些参考代码和一系列具体的测试用例描述，请完成单元测试的代码编写。
每个测试函数都应该是独立且可执行的。

请确保与参考代码使用相同的测试框架、模拟对象库、断言库等，并采取相似的模拟策略、判断策略等。

目标函数是 `{function_name}`，该函数位于文件 {file_path}。

以下是与该函数相关的源代码：

{relevant_content}

{reference_content}

以下是测试用例列表：

{test_cases_str}


请按照以下格式回复：

测试用例 1. <测试用例1的原始描述>

<测试用例1对应的测试函数代码>

测试用例 2. <测试用例2的原始描述>

<测试用例2对应的测试函数代码>
"""
