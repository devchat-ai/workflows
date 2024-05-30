# 工作流定义文件规范

工作流定义文件固定使用文件名`command.yml`，用来配置工作流的相关信息、使用内置变量、运行脚本等。

## 工作流属性

### `description`

工作流的描述信息，将在DevChat聊天栏的Workflow List中展示。

示例:
```yaml
description: Say hello to the world
```

### `steps`

工作流的执行步骤，包含一个或多个`run`字段，用于依次运行命令或脚本。运行输出的内容将被视为 Markdown 格式的消息显示在聊天窗口中。

> **NOTE:** 当前版本执行命令的工作目录为编辑器所打开的的工作区目录，不久后命令的工作目录将会变更为用户目录（`~`）。

示例:
```yaml
steps:
  - run: echo "Hello World!"
  - run: date +"%Y-%m-%d %H:%M:%S"
```

### `help`

定义工作流的帮助文档（Markdown格式），通过 `/<workflow_name> --help` 在聊天窗口中显示帮助文档内容。

`help`的形式为以下之一：
- 单个字符串：帮助文档的相对于此`command.yml`的文件路径。
- `key: value` 对：多语言的帮助文档，`key`为语言代码，`value`为帮助文档的相对于此`command.yml`的文件路径。可通过`--help.{lang}`显示指定语言对应的文档。

示例一:
```yaml
help: readme.md
```

以下命令均将显示`readme.md`的内容：
```
/<workflow_name> --help
/<workflow_name> --help.en
/<workflow_name> --help.zh
/<workflow_name> --help.xxx
```

示例二:
```yaml
help:
  en: 1.md
  zh: 2.md
```

```
/<workflow_name> --help      # 默认显示第一个文档，即`1.md`
/<workflow_name> --help.en   # 显示`1.md`
/<workflow_name> --help.zh   # 显示`2.md`
/<workflow_name> --help.xxx  # 默认显示第一个文档，即`1.md`
```

### `workflow_python`

DevChat Workflow Engine为执行 Python 脚本提供了更多便利。可通过`workflow_python`为当前工作流创建独立的Python环境、安装依赖（需能访问公网）。

- `workflow_python.env_name`(Optional)
  - Python环境名称，用于区分不同工作流的Python环境。默认与工作流同名。
- `workflow_python.version`
  - 指定该环境的Python版本。
- `workflow_python.dependencies`
  - Python依赖包文件（即`requirements.txt`）相对于此`command.yml`的文件路径，用于安装Python依赖。
  - 关于`requirements.txt`的更多信息，请参考[Python官方文档](https://pip.pypa.io/en/stable/user_guide/#requirements-files)。
  
示例，创建一个名为`my_env`的Python环境用于在当前工作流中运行Python脚本：
```yaml
workflow_python:
  env_name: my_env
  version: 3.8
  dependencies: dep.txt
```

> **拓展：** [无法访问公网时，需手动配置workflow_python](user_settings.md#external_workflow_python)


## 内置变量

### `$input`

`$input`用于获取用户在DevChat聊天栏中的输入（`/<workflow_name>`之后的部分）。

使用示例
```yaml
steps:
  - run: echo $input
```

### `$command_path`

`$command_path`当前工作流目录的路径。可用于引用工作流目录下的文件。

使用示例
```yaml
steps:
  - run: cat $command_path/README.md
```

### `$devchat_python`

DevChat Workflow Engine内置Python，可用来执行简单的Python脚本（无特殊包依赖）。

使用示例
```yaml

steps:
  - run: $devchat_python -c "print('Hello World!')"
  - run: $devchat_python $command_path/main.py
```

### `$workflow_python`

当前工作流独立的Python环境，必须定义了`workflow_python`属性后才可使用。

使用示例
```yaml
workflow_python:
    env_name: my-py
    version: 3.12.0
    dependencies: my_dep.txt
steps:
  - run: $workflow_python $command_path/main.py
```


## 其他

### 路径表示方式

在`command.yml`中，表示路径应使用POSIX风格，即，使用正斜杠`/`作为路径分隔符。
