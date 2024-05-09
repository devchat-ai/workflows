# ruff: noqa: E501
# Don not limit the length of each line of the prompts.


PROPOSE_TEST_PROMPT = """
You're an advanced AI test case generator.
Given a user prompt and a target function, propose detailed test cases for the function based on the prompt, categorizing each as either a 'happy path' or an 'edge case'.

The user prompt is as follows:

{user_prompt}

The target function is {function_name}, located in the file {file_path}.

Here's the relevant source code of the function:

{relevant_content}

For each test case, provide a description that includes:
- A brief explanation of the test's purpose
- The specific conditions being tested.
- The expected outcome the test is verifying.
Each description should be a single sentence, as concise as possible.

Categorize each test case as:
- 'happy path': Tests the function with typical inputs and standard conditions, ensuring it performs as expected in normal use.
- 'edge case': Tests the function with atypical inputs or in unusual conditions, checking its robustness and error handling.

You don't have to write the test cases in code, just describe them in plain {chat_language}.

Aim to generate 3 'happy path' test cases and 3 'edge case' test cases, totaling 6 test cases.

Answer in JSON format:
{{
    "test_cases": [
        {{"description": "<describe test case 1 in {chat_language}>", "category": "happy path"}},
        ...
        {{"description": "<describe test case 4 in {chat_language}>", "category": "edge case"}},
        ...
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
Given a target function, some relevant source code, some reference test code, and a list of specific test case descriptions, write the test cases in code.
Each test case should be self-contained and close to executable as possible.

The target function is {function_name}, located in the file {file_path}.
Here's the relevant source code of the function:

{relevant_content}

{reference_content}

Here's the list of test case descriptions:

{test_cases_str}

Answer in {chat_language} with the following requirements:

Basic requirements

1. Put all the test code in a single code block.
2. Use the content of the reference test cases as a model if possible. Ensuring you use the same test framework and mock library, and apply comparable mocking strategies and best practices.
3. Describe the test cases in comment in the same order as the list above.
4. Include libraries at the top of the code block if needed.
5. If two or more test cases share the same setup, you should reuse the setup code.
6. If two or more test cases share the same test logic, you should reuse the test logic.
7. Use TODO comments or FIXME comments to indicate any missing parts of the code or any parts that need to be improved.

{additional_requirements}

"""
