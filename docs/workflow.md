# 工作流开发指南

在[快速入门](./quickstart.md)中，我们创建了一个简单的DevChat Workflow。本文将展示更丰富的 DevChat Workflow 特性。


## 多层级 Workflow

工作流可随目录结构进行多层级扩展，用`.`连接各级目录组成子工作流的完整名称。

例如，对于如下`custom`目录结构：

```
custom
├── config.yml
└── demo
    ├── lang
    │   ├── command.yml
    │   ├── en
    │   │   ├── command.yml
    │   │   └── main.py
    │   ├── jp
    │   │   ├── command.yml
    │   │   └── main.py
    │   └── main.py
    └── my_hello
        └── command.yml
```
当`demo`被注册为命名空间后，4个`command.yml`文件分别对应4个工作流：
- `/lang`
- `/lang.en`
- `/lang.jp`
- `/my_hello`

`/lang.en` 和 `/lang.jp` 便是`lang`下的子工作流。

TODO: 引用example 

### 多层级 Workflow 的 workflow_python 环境共用

上级目录中`command.yml`里定义的`workflow_python`环境可在其子工作流中直接使用。子工作流也可另行定义自己单独的`workflow_python`环境。

但上级工作流无法使用子工作流中定义的`workflow_python`环境。`workflow_python`环境也不支持跨目录引用。


TODO: 引用example


## ChatMark: 在消息中进行用户交互的标记语法

语法介绍：
- [chatmark](https://github.com/devchat-ai/devchat-docs/blob/main/docs/specs/chatmark.md)


### Python 封装

为了方便开发者在 Python 脚本中使用 ChatMark，我们提供了 ChatMark Python 封装。
- [ChatMark Python](../lib/chatmark/README.md)
- [使用示例](../lib/chatmark/chatmark_example/main.py)


## IDE Service Protocol：在工作流中与编辑器交互的协议

[IDE Service Protocol 介绍](https://merico.feishu.cn/wiki/A3LCwOUE8igbHRkhqE5cviJunyd)

TODO: 有些新接口没写到文档里，待补充


### Python 封装

为了方便开发者在 Python 脚本中使用 IDE Service，我们提供了IDE Service Python 封装。

- [IDE Service Python](../lib/ide_service/service.py)


## 其他示例

TODO: