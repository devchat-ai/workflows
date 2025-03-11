### new_pr

创建新的Pull Request。

#### 用途
- 自动生成PR标题和描述
- 简化代码审查流程

#### 使用方法
执行命令: `/github.new_pr [additional_info]`

- additional_info: 可选的附加信息

#### 操作流程
1. 获取当前分支信息和相关Issue
2. 生成PR标题和描述
3. 允许用户编辑PR内容
4. 创建Pull Request

#### 注意事项
- 确保当前分支有未合并的更改
- 需要有创建PR的权限