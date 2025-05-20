# /work_report

Generate user work report based on git issue and commit information

## Purpose

- Automatically generate work reports based on git activities
- Track and summarize issues and commits within a specified time period
- Provide a structured format for work reporting

## Usage Method

```shell
/work_report <date_description>
```

Example: `/work_report last week`

If no valid date parameters are provided, the system will default to generating a report from yesterday to today.

## Features

- Generates reports based on:
  - Issues created within the specified time period
  - Commits made within the specified time period by the author
- Uses a customizable template for report formatting
- Supports both English and Chinese documentation
- Automatically detects user's git username and repository information

## Report Content

The report includes:

- Time period covered
- List of issues worked on
- List of commits made
- Formatted according to the configured template

## Configuration

The report template can be customized by modifying the `template.md` file in the script directory. The template file is located at `~/.chat/scripts/community/work_report/template.md`.
