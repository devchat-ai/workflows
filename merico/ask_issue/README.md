### ask_issue

Automatically fix lint errors in code.

#### Purpose

This Command helps developers quickly identify and fix lint errors in code. It uses AI to analyze selected code lines, identify lint issues, and provide intelligent fix suggestions.

#### Usage Method

1. Select code lines containing lint errors in the IDE.
2. Run the Command: /ask_issue
3. The Command will automatically process the selected code and related lint diagnostic information.
4. AI will generate problem explanations and fix solutions.

#### Notes

- Before running the Command, ensure you have selected specific code lines containing lint errors.
- The Command prioritizes issues diagnosed by SonarLint.
- It only focuses on and fixes lint errors in the selected lines, and will not handle other potential issues.
- The AI-generated fix solution includes problem explanation and modified code snippets.
- The modified code is displayed in Markdown format, with sufficient context information for locating.

#### Additional Information

- This Command uses AI models for analysis and fix suggestions.
- Fix suggestions will consider the code context to ensure modifications do not affect the correctness of other parts.
- For complex lint errors, manual review of AI fix suggestions may be required.
