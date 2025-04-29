### test.api.config

Configure global and repository-related settings needed for the API testing workflow.

#### Purpose

- Configure server connection information (SERVER_URL, USERNAME, PASSWORD)
- Configure project-related information (PROJECT_ID, OPENAPI_URL, VERSION_URL)

#### Usage Method

Execute command: `/test.api.config`

#### Operation Process

1. Enter server URL (example: http://kagent.merico.cn:8000)
2. Enter username
3. Enter password
4. Enter project ID (example: 37)
5. Enter OpenAPI document URL (example: http://kagent.merico.cn:8080/openapi.json)
6. Enter version information URL (example: http://kagent.merico.cn:8080/version)
7. Save configuration information

#### Configuration Storage Location

- Global configuration (SERVER_URL, USERNAME, PASSWORD) is saved in `~/.chat/.workflow_config.json`
- Repository configuration (PROJECT_ID, OPENAPI_URL, VERSION_URL) is saved in the current repository's `.chat/.workflow_config.json`

#### Notes

- Password information should be kept secure and not disclosed
- After configuration is complete, other API testing workflows will automatically use these configuration settings
- To modify the configuration, simply run this command again
