import os
import sys

def list_files():
    aider_files_path = os.path.join('.chat', '.aider_files')
    
    # 确保.chat/.aider_files文件存在
    if not os.path.exists(aider_files_path):
        print("No files have been added to aider yet.")
        sys.exit(0)

    # 读取文件列表
    with open(aider_files_path, 'r') as f:
        files = [line.strip() for line in f]

    # 打印文件列表
    if files:
        print("Aider files:")
        for file in sorted(files):
            print(f"- {file}")
    else:
        print("No files found in aider.")

def main():
    list_files()

if __name__ == "__main__":
    main()