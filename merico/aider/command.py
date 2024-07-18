import os
import sys
import json
import subprocess

from devchat.ide import IDEService
from lib.chatmark import Button

GLOBAL_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".chat", ".workflow_config.json")

def save_config(config_path, item, value):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}

    config[item] = value
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def write_python_path_to_config():
    """
    Write the current system Python path to the configuration.
    """
    python_path = sys.executable
    save_config(GLOBAL_CONFIG_PATH, 'aider_python', python_path)
    print(f"Python path '{python_path}' has been written to the configuration.")

def get_aider_files():
    """
    从.chat/.aider_files文件中读取aider文件列表
    """
    aider_files_path = os.path.join('.chat', '.aider_files')
    if not os.path.exists(aider_files_path):
        return []
    
    with open(aider_files_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def run_aider(message, files):
    """
    运行aider命令
    """
    python = sys.executable
    model = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo-1106')
    
    cmd = [
        python,
        "-m",
        "aider",
        "--model",
        f"openai/{model}",
        "--yes",
        "--no-auto-commits",
        "--dry-run",
        "--no-pretty",
        "--message",
        message,
    ] + files

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    has_started = False
    aider_output = ""
    for line in process.stdout:
        if "run with --help" in line or 'run "aider --help"' in line:
            has_started = True
            continue
        if has_started:
            aider_output += line
            print(line, end="", flush=True)

    return_code = process.wait()

    if return_code != 0:
        for line in process.stderr:
            print(f"Error: {line.strip()}", file=sys.stderr)
        sys.exit(return_code)

    return aider_output

def apply_changes(changes, files):
    """
    应用aider生成的更改
    """
    changes_file = '.chat/changes.txt'
    os.makedirs(os.path.dirname(changes_file), exist_ok=True)
    with open(changes_file, 'w') as f:
        f.write(changes)

    python = sys.executable
    model = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo-1106')

    cmd = [
        python,
        "-m",
        "aider",
        "--model",
        f"openai/{model}",
        "--yes",
        "--no-auto-commits",
        "--apply",
        changes_file,
    ] + files

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    has_started = False
    for line in process.stdout:
        if "Model:" in line:
            has_started = True
            continue
        if has_started:
            print(line, end="", flush=True)

    return_code = process.wait()

    if return_code != 0:
        for line in process.stderr:
            print(f"Error: {line.strip()}", file=sys.stderr)
        sys.exit(return_code)

    os.remove(changes_file)

def main():
    """
    Main function to run the aider command.

    This function performs the following tasks:
    1. Checks for correct command-line usage
    2. Writes the current Python path to the configuration
    3. Retrieves the list of files to be processed
    4. Runs the aider command with the given message
    5. Applies the suggested changes
    6. Displays the differences in the IDE

    Usage: python command.py <message>
    """
    if len(sys.argv) < 2:
        print("Usage: python command.py <message>", file=sys.stderr)
        sys.exit(1)
    
    write_python_path_to_config()

    message = sys.argv[1]
    files = get_aider_files()

    if not files:
        print("No files added to aider. Please add files using 'aider.files.add' command.", file=sys.stderr)
        sys.exit(1)

    print("Running aider...\n", flush=True)
    changes = run_aider(message, files)

    if not changes:
        print("No changes suggested by aider.")
        sys.exit(0)

    print("\nApplying changes...\n", flush=True)
    
    # 保存原始文件内容
    original_contents = {}
    for file in files:
        with open(file, 'r') as f:
            original_contents[file] = f.read()

    # 应用更改
    apply_changes(changes, files)

    # 读取更新后的文件内容
    updated_contents = {}
    for file in files:
        with open(file, 'r') as f:
            updated_contents[file] = f.read()

    # 还原原始文件内容
    for file in files:
        with open(file, 'w') as f:
            f.write(original_contents[file])

    # 使用 IDEService 展示差异
    ide_service = IDEService()
    for index,file in enumerate(files):
        ide_service.diff_apply(file, updated_contents[file])
        if index < len(files) - 1:
            # 等待用户确认
            button = Button(
                [
                    "Show Next Changes",
                    "Cancel"
                ],
            )
            button.render()

            idx = button.clicked
            print("click button:", idx)
            if idx == 0:
                continue
            else:
                break

    print("Changes have been displayed in the IDE.")

if __name__ == "__main__":
    main()
