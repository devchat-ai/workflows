
需要输入参数，使用指南如下：

## 1.生成测试用例

点击函数头部"unit tests"按钮，触发代码分析。工作流会收集该函数相关的变量定义、相关测试文件等信息用于生成 6 个推荐的测试用例，包括 3 个正常路径，3 个边界条件。
![图片](https://deploy-script.merico.cn/devchat/workflow/unit_tests_1.png)

## 2.选择测试用例

当测试用例生成完毕，你可以选择你觉得有意义的测试用例，进行下一步操作。
![图片](https://deploy-script.merico.cn/devchat/workflow/unit_tests_2.png)

## 4.输入控制信息

如果你认为推荐的测试用例不能满足你的测试要求，也可以通过输入框补充你的测试需求。必要的话可以修改参考文件到你喜欢的文件。最后，补充一些要求，例如期望使用的测试框架等等。
![图片](https://deploy-script.merico.cn/devchat/workflow/unit_tests_3.png)
最后，点击 Submit 按钮开始生成单元测试。

## 5.生成测试代码

DevChat 会生成一份完整的文件，包含刚才选择的测试用例。一般情况下，这可能比较适合新文件的覆盖，当然你也可以拷贝其中的部分代码。
![图片](https://deploy-script.merico.cn/devchat/workflow/unit_tests_4.png)
代码块的右上角提供了一些便捷操作，包括插入代码、拷贝代码、查看代码变动等。
![图片](https://deploy-script.merico.cn/devchat/workflow/unit_tests_5.png)
选定代码以后，就可以进行单元测试的运行了。
