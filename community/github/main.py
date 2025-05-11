from lib.workflow.call import print_sub_workflows, workflow_call
from lib.workflow.decorators import check_config


@check_config(["github_token"])
def main(github_token: bool):
    print_sub_workflows()
    if not github_token:
        workflow_call("/github.config")


if __name__ == "__main__":
    main()
