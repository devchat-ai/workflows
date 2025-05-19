# /gitlab.work_report

Generate user weekly report based on gitlab issue and commit information

## Purpose

- Automatically generate work reports based on GitLab activities
- Track and summarize issues and commits within a specified time period
- Provide a structured format for work reporting

## Usage Method

1. Execute the command with date range:

   ```shell
   /gitlab.work_report <start_date> <end_date>
   ```

   Example: `/gitlab.work_report 2024-03-01 2024-03-07`

2. Or execute without parameters to generate yesterday's report:

   ```shell
   /gitlab.work_report
   ```

## Features

- Generates reports based on:
  - Issues created/updated within the specified time period
  - Commits made within the specified time period
- Uses a customizable template for report formatting
- Supports both English and Chinese documentation
- Automatically detects user's GitLab username and repository information

## Report Content

The report includes:

- Time period covered
- List of issues worked on
- List of commits made
- Formatted according to the template specified in configuration

## Configuration

The report template can be customized by setting the `gitlab_work_report_template_path` in the global configuration.
