# ruff: noqa: E501
# Don not limit the length of each line of the prompts.


PROPOSE_TEST_PROMPT = """
You're an advanced AI test case generator.
Given a user prompt and a target function, propose test cases for the function based on the prompt.

The user prompt is as follows:

{user_prompt}

The target function is {function_name}, located in the file {file_path}.

Here's the relevant source code of the function:

{relevant_content}

Propose each test case with a one-line description of what behavior it tests.
You don't have to write the test cases in code, just describe them in plain {chat_language}.
Do not generate more than 6 test cases.

Answer in JSON format:
{{
    "test_cases": [
        {{"description": "<describe test case 1 in {chat_language}>"}},
        {{"description": "<describe test case 2 in {chat_language}>"}},
    ]
}}
"""


FIND_REFERENCE_PROMPT = """
Identify a suitable reference test file that can be used as a guide for writing test cases
for the function {function_name}, located in the file {file_path}. 
The reference should provide a clear example of best practices in testing functions of a similar nature.
"""


WRITE_TESTS_PROMPT = """
You're an advanced AI test case generator.
Given a target function, some reference test code, and a list of specific test case descriptions, write the test cases in code.
Each test case should be self-contained and executable.
Use the content of the reference test cases as a model, ensuring you use the same test framework and mock library,
and apply comparable mocking strategies and best practices.


The target function is {function_name}, located in the file {file_path}.
Here's the relevant source code of the function:

{relevant_content}

{reference_content}

Here's the list of test case descriptions:

{test_cases_str}

Answer in the following format in {chat_language}:

Test Case 1. <original test case 1 description>

<test case 1 code>

Test Case 2. <original test case 2 description>

<test case 2 code>
"""
