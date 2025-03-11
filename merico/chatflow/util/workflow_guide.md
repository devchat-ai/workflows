一个工作流对应一个目录，目录可以进行嵌套，每个工作流在UI视图中对应了一个斜杠命令，例如/github.commit。

github工作流目录结构简化后示意如下：
github
  ｜-- commit
        |-- command.yml
        |-- command.py

        |-- README.md
  ｜-- new_pr
        |-- command.yml
        |-- command.py
   ......

"command.yml"文件定义了工作流命令的元信息，例如命令的名称、描述、参数等。
"command.py"文件定义了工作流命令的实现逻辑。

拿一个hello world工作流命令为例，目录结构如下：
helloworld
  ｜-- command.yml
  ｜-- command.py
  ｜-- README.md

"command.yml"文件内容如下：
```yaml
description: Hello Workflow, use as /helloworld <name>
input: required
steps:
  - run: $devchat_python $command_path/command.py "$input"
````
"command.py"文件内容如下：
```python
import sys
print(sys.argv[1])
```

使用一个工作流时，在DevChat AI智能问答视图中输入斜杠命令，例如/helloworld <name>，即可执行该工作流命令。/helloworld表示对应系统可用的工作流。<name>表示工作流的输入，是可选的，如果工作流定义中input为required，则必须输入，否则可以不输入。

工作流命令有重载优先级，merico目录下工作流 < community目录下工作流 < custom目录下工作流。
例如，如果merico与community目录下都有github工作流，那么在DevChat AI智能问答视图中输入/github命令时，会优先执行community目录下的github工作流命令。

在custom目录下，通过config.yml文件定义custom目录下的工作流目录。例如：
namespaces:
  - bobo
那么custom/bobo就是一个工作流存储目录，可以在该目录下定义工作流命令。
例如：
custom/bobo
        | ---- hello
                 |------ command.yml
                 |------ command.py
那么custom/bobo/hello对应的工作流命令就是/hello.

