### list_issue_tasks

列出指定Issue中的任务列表。

#### 用途
- 查看Issue中的子任务
- 跟踪任务进度

#### 使用方法
执行命令: `/github.list_issue_tasks <issue_url>`

#### 操作流程
1. 获取指定Issue的信息
2. 解析Issue内容中的任务列表
3. 显示任务列表

#### 注意事项
- 需要提供有效的Issue URL
- 任务应以特定格式在Issue中列出(如: - [ ] 任务描述)