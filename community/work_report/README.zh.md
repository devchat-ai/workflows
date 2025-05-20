# /work_report

根据用户 git issue 信息和 commit 信息生成用户工作报告

## 功能目的

- 基于 git 活动自动生成工作报告
- 追踪和总结指定时间段内的 issues 和 commits
- 提供结构化的工作报告格式

## 使用方法

```shell
/work_report <日期描述>
```

示例：`/work_report 上周`

如果没有提供有效的日期参数，系统将默认生成从昨天到今天的报告。

## 功能特点

- 报告生成基于：
  - 指定时间段内创建的 issues
  - 指定时间段内作者提交的 commits
- 使用可自定义的报告模板
- 支持中英文文档
- 自动检测用户的 git 用户名和仓库信息

## 报告内容

报告包含：

- 报告时间范围
- 处理的 issues 列表
- 提交的 commits 列表
- 根据配置的模板格式化输出

## 配置说明

可以修改脚本目录中的 `template.md` 文件来自定义报告模板。模板文件位于 `~/.chat/scripts/community/work_report/template.md`。
