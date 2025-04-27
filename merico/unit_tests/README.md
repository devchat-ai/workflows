### unit_tests

This Command is used to automatically generate unit tests for selected functions.

#### Purpose

- Quickly generate unit test cases for functions
- Improve code test coverage
- Save time on manually writing test cases

#### Usage Method

1. In the IDE, place the cursor on the function that needs unit tests
2. Click the **DevChat: unit tests** button on the function header

#### Operation Process

1. Click the **DevChat: unit tests** button on the function header
2. In the popup dialog, select the type of test cases to generate:
   - Happy Path test cases
   - Edge Case test cases
3. (Optional) Type additional control information:
   - Supplementary test cases
   - Reference files
   - Additional prompts
4. Click the submit button
5. Wait for test case generation to complete

#### Notes

1. Ensure that the cursor is positioned correctly on the function before executing the Command
2. Generated test cases may require further adjustment and refinement
3. For complex functions, more context information may need to be provided to generate more accurate test cases

#### Additional Information

- The language of the test cases will remain consistent with the original code
- This Command uses AI technology to generate test cases, which may require some processing time
- Generated test cases include both normal paths and edge cases to improve test coverage

#### Tips

Using the unit_tests Command can quickly create a basic unit test framework, but it is recommended that developers carefully review and supplement the generated test cases to ensure they comprehensively cover various scenarios of the function.

As shown in the figure:

![Image](https://deploy-script.merico.cn/devchat/workflow/readme_unit_tests.gif)
