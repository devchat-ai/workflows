# flake8: noqa: E402
import os
import re
import sys
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "libs"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "libs"))
sys.path.append(os.path.dirname(__file__))

from chatmark import Checkbox, Form, TextEditor  # noqa: E402
from llm_api import chat_completion_stream  # noqa: E402
from ide_services.services import log_info


# Read the prompt from the diffCommitMessagePrompt.txt file
def read_prompt_from_file(filename):
    """
    Reads the content of a file and returns it as a string.

    This function is designed to read a prompt message from a text file.
    It expects the file to be encoded in UTF-8 and will strip any leading
    or trailing whitespace from the content of the file. If the file does
    not exist or an error occurs during reading, the function logs an error
    message and exits the script.

    Parameters:
    - filename (str): The path to the file that contains the prompt message.

    Returns:
    - str: The content of the file as a string.

    Raises:
    - FileNotFoundError: If the file does not exist.
    - Exception: If any other error occurs during file reading.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        log_info(
            f"File {filename} not found. "
            "Please make sure it exists in the same directory as the script."
        )
        sys.exit(1)
    except Exception as e:
        log_info(f"An error occurred while reading the file {filename}: {e}")
        sys.exit(1)


# Read the prompt content from the file
script_path = os.path.dirname(__file__)
PROMPT_FILENAME = os.path.join(script_path, "diffCommitMessagePrompt.txt")
PROMPT_COMMIT_MESSAGE_BY_DIFF_USER_INPUT = read_prompt_from_file(PROMPT_FILENAME)
prompt_commit_message_by_diff_user_input_llm_config = {'model': os.environ.get('LLM_MODEL', 'gpt-3.5-turbo-1106')}


language = ""


def assert_value(value, message):
    """
    判断给定的value是否为True，如果是，则输出指定的message并终止程序。

    Args:
        value: 用于判断的值。
        message: 如果value为True时需要输出的信息。

    Returns:
        无返回值。

    """
    if value:
        print(message, file=sys.stderr, flush=True)
        sys.exit(-1)


def decode_path(encoded_path):
    octal_pattern = re.compile(r"\\[0-7]{3}")

    if octal_pattern.search(encoded_path):
        bytes_path = encoded_path.encode("utf-8").decode("unicode_escape").encode("latin1")
        decoded_path = bytes_path.decode("utf-8")
        return decoded_path
    else:
        return encoded_path


def get_modified_files():
    """
    获取当前修改文件列表以及已经staged的文件列表

    Args:
        无

    Returns:
        tuple: 包含两个list的元组，第一个list包含当前修改过的文件，第二个list包含已经staged的文件
    """
    """ 获取当前修改文件列表以及已经staged的文件列表"""
    output = subprocess.check_output(["git", "status", "-s", "-u"], text=True, encoding="utf-8")
    lines = output.split("\n")
    modified_files = []
    staged_files = []

    def strip_file_name(file_name):
        file = file_name.strip()
        if file.startswith('"'):
            file = file[1:-1]
        return file

    for line in lines:
        if len(line) > 2:
            status, filename = line[:2], decode_path(line[3:])
            # check wether filename is a directory
            if os.path.isdir(filename):
                continue
            modified_files.append(os.path.normpath(strip_file_name(filename)))
            if status[0:1] == "M" or status[0:1] == "A":
                staged_files.append(os.path.normpath(strip_file_name(filename)))
    return modified_files, staged_files


def get_marked_files(modified_files, staged_files):
    """
    根据给定的参数获取用户选中以供提交的文件

    Args:
        modified_files (List[str]): 用户已修改文件列表
        staged_files (List[str]): 用户已staged文件列表

    Returns:
        List[str]: 用户选中的文件列表
    """
    # Create two Checkbox instances for staged and unstaged files
    staged_checkbox = Checkbox(staged_files, [True] * len(staged_files))

    unstaged_files = [file for file in modified_files if file not in staged_files]
    unstaged_checkbox = Checkbox(unstaged_files, [False] * len(unstaged_files))

    # Create a Form with both Checkbox instances
    form = Form(
        [
            "Select the files you've changed that you wish to include in this commit, "
            "then click 'Submit'.\n\nStaged:\n\n",
            staged_checkbox,
            "Unstaged:\n\n",
            unstaged_checkbox,
        ]
    )

    # Render the Form and get user input
    form.render()

    # Retrieve the selected files from both Checkbox instances
    selected_staged_files = [staged_files[idx] for idx in staged_checkbox.selections]
    selected_unstaged_files = [unstaged_files[idx] for idx in unstaged_checkbox.selections]

    # Combine the selections from both checkboxes
    selected_files = selected_staged_files + selected_unstaged_files

    return selected_files


def rebuild_stage_list(user_files):
    """
    根据用户选中文件，重新构建stage列表

    Args:
        user_files: 用户选中的文件列表

    Returns:
        None

    """
    # Unstage all files
    subprocess.check_output(["git", "reset"])
    # Stage all user_files
    for file in user_files:
        os.system(f'git add "{file}"')


def get_diff():
    """
    获取暂存区文件的Diff信息

    Args:
        无

    Returns:
        bytes: 返回bytes类型，是git diff --cached命令的输出结果

    """
    return subprocess.check_output(["git", "diff", "--cached"])


def generate_commit_message_base_diff(user_input, diff):
    """
    根据diff信息，通过AI生成一个commit消息

    Args:
        user_input (str): 用户输入的commit信息
        diff (str): 提交的diff信息

    Returns:
        str: 生成的commit消息

    """
    global language
    language_prompt = (
        "You must response commit message in chinese。\n" if language == "chinese" else ""
    )
    prompt = PROMPT_COMMIT_MESSAGE_BY_DIFF_USER_INPUT.replace("{__DIFF__}", f"{diff}").replace(
        "{__USER_INPUT__}", f"{user_input + language_prompt}"
    )
    # if len(str(prompt)) > 20000:
    #     print(
    #         "Due to the large size of the diff data, "
    #         "generating a commit message through AI would be very costly, therefore, "
    #         "it is not recommended to use AI for generating the description. "
    #         "Please manually edit the commit message before submitting."
    #     )
    #     print(prompt, file=sys.stderr, flush=True)
    #     return {"content": ""}

    messages = [{"role": "user", "content": prompt}]
    response = chat_completion_stream(
        messages, prompt_commit_message_by_diff_user_input_llm_config
    )
    assert_value(not response, "")
    return response


def display_commit_message_and_commit(commit_message):
    """
    展示提交信息并提交。

    Args:
        commit_message: 提交信息。

    Returns:
        None。

    """
    print(("I've drafted a commit message for the code changes you selected. "
          "You can edit this message in the widget below. After confirming "
          "the message, click 'Commit', and I will proceed with the commit "
          "using this message.\n\n"))
    text_editor = TextEditor(commit_message)
    text_editor.render()

    new_commit_message = text_editor.new_text
    if not new_commit_message:
        return
    subprocess.check_output(["git", "commit", "-m", new_commit_message])


def check_git_installed():
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        print("Git is not installed on your system.", file=sys.stderr, flush=True)
    except FileNotFoundError:
        print("Git is not installed on your system.", file=sys.stderr, flush=True)
    except Exception:
        print("Git is not installed on your system.", file=sys.stderr, flush=True)
    return False


def main():
    global language
    try:
        print(
            "I can help you generate a summary for your code commit. "
            "Please follow the steps below to complete the process.\n\n"
        )
        # Ensure enough command line arguments are provided
        if len(sys.argv) < 3:
            print("Usage: python script.py <user_input> <language>", file=sys.stderr, flush=True)
            sys.exit(-1)

        user_input = sys.argv[1]
        language = sys.argv[2]

        if not check_git_installed():
            sys.exit(-1)

        print("Step 1/2: Please select the file to be submitted.", end="\n\n", flush=True)
        modified_files, staged_files = get_modified_files()
        if len(modified_files) == 0:
            print("No files to commit.", file=sys.stderr, flush=True)
            sys.exit(-1)

        selected_files = get_marked_files(modified_files, staged_files)
        if not selected_files:
            print("No files selected, commit aborted.")
            return

        rebuild_stage_list(selected_files)

        print(
            "Step 2/2: Generating commit message ...",
            end="\n\n",
            flush=True,
        )
        diff = get_diff()
        commit_message = generate_commit_message_base_diff(user_input, diff)

        # TODO
        # remove Closes #IssueNumber in commit message
        commit_message["content"] = commit_message["content"].replace("Closes #IssueNumber", "")

        display_commit_message_and_commit(commit_message["content"])
        print("Commit completed.", flush=True)
        sys.exit(0)
    except Exception as err:
        print("Exception:", err, file=sys.stderr, flush=True)
        sys.exit(-1)


if __name__ == "__main__":
    main()
