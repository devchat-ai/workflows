from .rpc import rpc_call


@rpc_call
def get_lsp_brige_port():
    pass


@rpc_call
def install_python_env(command_name: str, requirements_file: str) -> str:
    pass


@rpc_call
def update_slash_commands():
    pass


@rpc_call
def ide_language() -> str:
    pass


@rpc_call
def log_info(message: str):
    pass


@rpc_call
def log_warn(message: str):
    pass


@rpc_call
def log_error(message: str):
    pass
