from lib.workflow.call import print_sub_workflows, workflow_call
from lib.workflow.decorators import check_config


@check_config(["gitlab_token"])
def main(gitlab_token: bool):
    print_sub_workflows()
    if not gitlab_token:
        workflow_call("/gitlab.config")


if __name__ == "__main__":
    main()
