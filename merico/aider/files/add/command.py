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
        return os.path.isabs(normalized_path) or not os.path.dirname(normalized_path) == normalized_path
    except Exception:
        return False

def add_file(file_path):
    # 1. 检查是否为有效的文件路径形式
    if not is_valid_path(file_path):
        print(f"Error: '{file_path}' is not a valid file path format.", file=sys.stderr)
        sys.exit(1)

    # 获取绝对路径
    abs_file_path = file_path.strip()

    # 2. 将新增文件路径存储到.chat/.aider_files文件中
    aider_files_path = os.path.join('.chat', '.aider_files')
    
    # 确保.chat目录存在
    os.makedirs(os.path.dirname(aider_files_path), exist_ok=True)

    # 读取现有文件列表
    existing_files = set()
    if os.path.exists(aider_files_path):
        with open(aider_files_path, 'r') as f:
            existing_files = set(line.strip() for line in f)

    # 添加新文件
    existing_files.add(abs_file_path)

    # 写入更新后的文件列表
    with open(aider_files_path, 'w') as f:
        for file in sorted(existing_files):
            f.write(f"{file}\n")

    print(f"Added '{abs_file_path}' to aider files.")
    print("\nCurrent aider files:")
    for file in sorted(existing_files):
        print(f"- {file}")

def main():
    if len(sys.argv) != 2 or sys.argv[1].strip() == "":
        print("Usage: /aider.files.add <file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    add_file(file_path)

if __name__ == "__main__":
    main()