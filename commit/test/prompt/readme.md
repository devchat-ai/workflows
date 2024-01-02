
## Overview

This README provides information about the workflow used for generating commit messages based on commit differences. The workflow involves recording prompts, defining test cases, and running scripts to process these cases.

## File Structure

- **Prompt Record File**: `/Users/admin/.chat/workflows/org/commit/diffCommitMessagePrompt.txt`
  - This file contains the prompts that are used to generate commit messages.
  
- **Test Cases File**: `/Users/admin/.chat/workflows/org/commit/test/prompt/commit_message_tests.yaml`
  - This YAML file holds the test cases for the commit message generation tests. Each test case includes the `commit_url` which points to the specific commit differences to be used for generating the commit message.
  
- **Test Script**: `/Users/admin/.chat/workflows/org/commit/test/prompt/commit_message_run.py`
  - This is the Python script that processes the test cases. It fetches the commit differences from the provided `commit_url` and generates the commit messages accordingly.
  
- **Test Configuration File**: `/Users/admin/.chat/workflows/org/commit/test/prompt/commit_message_prompt_config.yaml`
  - This YAML file provides the overall description of the tests and configurations needed for the test execution.

## Test Execution

To execute the tests for commit message generation, use the following command:

```bash
npx promptfoo eval -c commit/test/prompt/commit_message_prompt_config.yaml
```

This command will run the tests as defined in the `commit_message_prompt_config.yaml` file.

## Viewing Test Results

After running the tests, you can display the results using the command below:

```bash
npx promptfoo view
```

This command will present the outcomes of the tests, allowing you to review the generated commit messages and their respective test cases.

## Dependency Installation

Before you can run the tests for commit message generation, you need to install the necessary dependencies. This involves setting up both Node.js and Python environments. Follow the steps below to install the dependencies.

### Node.js Dependency

To install the `promptfoo` tool using `npx`, run the following command:

```bash
npx promptfoo@latest
```

This command will ensure that you are using the latest version of `promptfoo`.

### Python Dependencies

The test script requires certain Python packages to be installed. To install these dependencies, navigate to the directory containing the `requirements.txt` file and run:

```bash
pip install -r commit/test/prompt/requirements.txt
```

This will install all the Python packages listed in the `requirements.txt` file, which are necessary for the test script to function correctly.

After completing these steps, you should have all the required dependencies installed and be ready to proceed with the test execution as described in the **Getting Started** section of this README.


## Getting Started

To get started with the commit message generation workflow:

1. Ensure you have `npx` and `promptfoo` installed and configured on your system.
2. Navigate to the directory containing the workflow files.
3. Review and update the test cases in `commit_message_tests.yaml` as needed.
4. Run the test execution command to generate commit messages.
5. Use the test results viewing command to analyze the results.

For any additional help or to report issues, please refer to the project's issue tracker or contact the repository administrator.