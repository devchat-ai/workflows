# 用户设置`user_settings.yml`

`~/.chat/scripts/user_settings.yml`文件用于配置用户的个性化设置。

## `external_workflow_python`
 
在不能访问公网的环境下，DevChat Workflow Engine无法按照`command.yml`中定义的`workflow_python`自动创建 Python 环境。此时，需要用户自行准备好相应 Python 环境，并在`external_workflow_python`中配置。


- `external_workflow_python.env_name`: 应与`command.yml`中的`workflow_python.env_name`一致。表示下面指定的 Python 将被用于<env_name>环境。
- `external_workflow_python.python_bin`: 为用户准备的 Python 路径，用来替代`$workflow_python`运行 Python 脚本。


#### 示例

某工作流定义了独立的`workflow_python`配置：

```yaml
workflow_python:
  env_name: foo-env
  version: 3.12
  dependencies: requirements.txt
```

在无法访问公网的环境下，需要用户（用其他手段）自行准备一个 Python 版本为3.12、并安装了`requirements.txt`中依赖包的环境。

然后在`user_settings.yml`添加如下配置：

```yaml
external_workflow_python:
  - env_name: foo-env
    python_bin: path/to/the/user/prepared/python
```
