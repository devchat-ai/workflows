### aider.files.add

添加文件到aider处理列表中。

用法：
/aider.files.add <file_path>

参数：
- <file_path>: 要添加的文件路径（必需）

描述：
这个命令将指定的文件添加到aider的处理列表中。添加后，该文件将被包含在后续的aider操作中。

注意：
- 文件路径必须是有效的格式。
- 如果文件已经在列表中，它不会被重复添加。
- 添加成功后，会显示当前aider文件列表。

示例：
/aider.files.add src/main.py