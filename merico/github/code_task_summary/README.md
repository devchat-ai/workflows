### code_task_summary

根据当前分支或指定的Issue,生成代码任务摘要。

#### 用途
- 自动生成简洁的代码任务描述
- 帮助开发者快速理解任务要点
- 用于更新项目配置或文档

#### 使用方法
执行命令: `/github.code_task_summary [issue_url]`

- 如不提供issue_url,将基于当前分支名称提取Issue信息
- 如提供issue_url,将直接使用该Issue的内容

#### 操作流程
1. 获取Issue信息
2. 生成代码任务摘要
3. 允许用户编辑摘要
4. 更新项目配置文件

#### 注意事项
- 确保Git仓库配置正确
- 需要有效的GitHub Token以访问API