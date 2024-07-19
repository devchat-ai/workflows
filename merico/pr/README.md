# pr 命令

pr命令是一个用于处理Pull Requests (PRs)的主命令。它本身不执行具体操作，而是通过子命令来完成特定功能。

## 可用子命令

1. pr.review - 生成PR代码评审描述
2. pr.improve - 生成PR的代码建议
3. pr.describe - 生成PR描述
4. pr.custom_suggestions - 生成PR的自定义代码建议

## 使用方法

要使用pr命令的功能，请使用以下格式调用相应的子命令：

/pr.<子命令> <PR_URL>

例如：
- /pr.review https://github.com/devchat-ai/devchat/pull/301
- /pr.improve https://github.com/devchat-ai/devchat/pull/301
- /pr.describe https://github.com/devchat-ai/devchat/pull/301
- /pr.custom_suggestions https://github.com/devchat-ai/devchat/pull/301

## 子命令说明

1. pr.review: 分析PR并生成代码评审描述，帮助审阅者快速了解PR的内容和影响。

2. pr.improve: 分析PR并提供代码改进建议，帮助开发者优化其代码。

3. pr.describe: 自动生成PR的描述，总结PR的主要变更和目的。

4. pr.custom_suggestions: 根据特定需求生成自定义的PR代码建议。

请根据您的具体需求选择适当的子命令。每个子命令都专注于PR处理的不同方面，帮助您更高效地管理和改进Pull Requests。