# /gitlab.work_report

根据用户 gitlab issue 信息和 commit 信息生成用户周日报

## 功能目的

- 基于 GitLab 活动自动生成工作报告
- 追踪和总结指定时间段内的 issues 和 commits
- 提供结构化的工作报告格式

## 使用方法

1. 带日期范围执行命令：

   ```shell
   /gitlab.work_report <开始日期> <结束日期>
   ```

   示例：`/gitlab.work_report 2024-03-01 2024-03-07`

2. 不带参数执行命令（生成昨天的报告）：

   ```shell
   /gitlab.work_report
   ```

## 功能特点

- 报告生成基于：
  - 指定时间段内创建/更新的 issues
  - 指定时间段内的 commits
- 使用可自定义的报告模板
- 支持中英文文档
- 自动检测用户的 GitLab 用户名和仓库信息

## 报告内容

报告包含：

- 报告时间范围
- 处理的 issues 列表
- 提交的 commits 列表
- 根据配置的模板格式化输出

## 配置说明

可以通过全局配置中的 `gitlab_work_report_template_path` 来自定义报告模板。
