### test.api.config

配置API测试工作流所需的全局和仓库相关设置。

#### 用途
- 配置服务器连接信息（SERVER_URL, USERNAME, PASSWORD）
- 配置项目相关信息（PROJECT_ID, OPENAPI_URL, VERSION_URL）

#### 使用方法
执行命令: `/test.api.config`

#### 操作流程
1. 输入服务器URL（例如: http://kagent.merico.cn:8000）
2. 输入用户名
3. 输入密码
4. 输入项目ID（例如: 37）
5. 输入OpenAPI文档URL（例如: http://kagent.merico.cn:8080/openapi.json）
6. 输入版本信息URL（例如: http://kagent.merico.cn:8080/version）
7. 保存配置信息

#### 配置信息存储位置
- 全局配置（SERVER_URL, USERNAME, PASSWORD）保存在 `~/.chat/.workflow_config.json`
- 仓库配置（PROJECT_ID, OPENAPI_URL, VERSION_URL）保存在当前仓库的 `.chat/.workflow_config.json`

#### 注意事项
- 密码信息应妥善保管，不要泄露
- 配置完成后，其他API测试工作流将自动使用这些配置信息
- 如需修改配置，重新运行此命令即可