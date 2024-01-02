#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR=$(dirname "$0")
TEST_DIR="${SCRIPT_DIR}"
REQUIREMENTS_FILE="${TEST_DIR}/requirements.txt"
CONFIG_FILE="${TEST_DIR}/commit_message_prompt_config.yaml"

# 安装Node.js依赖
echo "Installing promptfoo using npx..."
npx promptfoo@latest

# 检查Python是否安装
if ! command -v python3 &> /dev/null
then
    echo "Python could not be found, please install Python 3."
    exit 1
fi

# 安装Python依赖
echo "Installing Python dependencies..."
pip3 install -r ${REQUIREMENTS_FILE}

# 执行测试用例
echo "Running test cases..."
npx promptfoo eval -c ${CONFIG_FILE}

# 打开测试结果视图
echo "Opening test results view..."
npx promptfoo view

# 执行结束
echo "Test execution and result viewing completed."