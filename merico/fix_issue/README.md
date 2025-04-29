### fix_issue

Automatically fix lint errors in code.

Usage:
/fix_issue

Description:
This Command helps developers automatically fix lint errors in code. It uses AI to analyze selected code lines, identify lint issues, and provide fix suggestions. Then, it automatically applies these fix suggestions and displays the changes in the IDE.

Steps:

1. Select code lines containing lint errors in the IDE.
2. Run the /fix_issue Command.
3. The Command will automatically retrieve the selected code, related lint diagnostic information, and call AI to generate fix solutions.
4. AI will provide problem explanations and fixed code.
5. The Command will automatically apply these fixes and display the changes in the IDE.

Notes:

- Ensure that you have selected code lines containing lint errors before running the Command.
- The Command will prioritize issues diagnosed by SonarLint.
- If aider Python is installed, the Command will use aider to execute AI access and apply changes.
- If aider Python is not installed, the Command will use the default implementation to generate and apply fixes.
- All changes will be displayed in the IDE in the form of a Diff View, and you can decide whether to accept these changes after reviewing them.
