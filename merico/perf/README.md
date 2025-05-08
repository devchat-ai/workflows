### refactor

This Command is used to rewrite selected code blocks according to user-specific requirements.

#### Purpose

- Refactor selected code based on specific needs
- Optimize code structure and readability
- Implement quick code improvements and adjustments

#### Usage Method

1. Select the code block that needs to be refactored in the IDE
2. Type `/refactor <refactoring requirements>` and press Enter
   Example: `/refactor Rewrite this function using async/await`

#### Operation Process

1. Select the code block that needs to be refactored
2. Execute the refactor Command, and provide specific refactoring requirements
3. Wait for the code refactoring to complete
4. A Diff View will automatically pop up, you can choose to accept or reject the changes

#### Notes

1. Ensure that you have selected the code block that needs to be refactored before executing the Command
2. Refactoring requirements should be as specific and clear as possible
3. This Command only modifies the selected code section, without affecting other code
4. The refactored code will maintain the original indentation format to ensure consistency with the existing code structure

#### Additional Information

- The language of the refactoring result will remain consistent with the original code
- This Command uses AI technology to generate refactoring suggestions, which may require some processing time
- Complex refactoring may require multiple attempts or manual adjustments

#### Tips

Using the refactor Command can quickly implement structural improvements to code, but please carefully review the refactored code to ensure it meets expectations and maintains the original functionality.

As shown in the figure:

![Image](https://deploy-script.merico.cn/devchat/workflow/readme_refactor.names.gif)
