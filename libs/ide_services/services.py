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
def ide_logging(level: str, message: str):
    """
    level: "info" | "warn" | "error" | "debug"
    """
    pass


@rpc_call
def get_document_symbols(abspath: str):
    pass


@rpc_call
def find_type_def_locations(abspath: str, line: int, character: int):
    pass


# NOTE: for compatibility, remove this after all usages are replaced with ide_logging
def log_info(message):
    return ide_logging("info", message)
