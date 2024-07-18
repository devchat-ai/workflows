import os
import sys


def is_valid_path(path):
    """
    检查路径是否为有效的文件路径形式
    """
    try:
        # 尝试规范化路径
        normalized_path = os.path.normpath(path)
        # 检查路径是否是绝对路径或相对路径
        return (
            os.path.isabs(normalized_path)
            or not os.path.dirname(normalized_path) == normalized_path
        )
    except Exception:
        return False


def remove_file(file_path):
    # 1. 检查是否为有效的文件路径形式
    if not is_valid_path(file_path):
        print(f"Error: '{file_path}' is not a valid file path format.", file=sys.stderr)
        sys.exit(1)

    # 获取绝对路径
    abs_file_path = file_path.strip()

    # 2. 从.chat/.aider_files文件中移除指定文件路径
    aider_files_path = os.path.join(".chat", ".aider_files")

    # 确保.chat目录存在
    if not os.path.exists(aider_files_path):
        print(f"Error: '{aider_files_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # 读取现有文件列表
    existing_files = set()
    with open(aider_files_path, "r") as f:
        existing_files = set(line.strip() for line in f)

    # 检查文件是否在列表中
    if abs_file_path not in existing_files:
        print(f"'{abs_file_path}' is not in aider files.")
        sys.exit(0)

    # 移除文件
    existing_files.remove(abs_file_path)

    # 写入更新后的文件列表
    with open(aider_files_path, "w") as f:
        for file in sorted(existing_files):
            f.write(f"{file}\n")

    print(f"Removed '{abs_file_path}' from aider files.")
    print("\nCurrent aider files:")
    for file in sorted(existing_files):
        print(f"- {file}")


def main():
    if len(sys.argv) != 2 or sys.argv[1].strip() == "":
        print("Usage: /aider.files.remove <file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    remove_file(file_path)


if __name__ == "__main__":
    main()
