import os
from functools import wraps
from typing import Dict

import requests

BASE_SERVER_URL = os.environ.get("DEVCHAT_IDE_SERVICE_URL", "http://localhost:3000")


def rpc_call(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if os.environ.get("DEVCHAT_IDE_SERVICE_URL", "") == "":
            # maybe in a test, user don't want to mock services functions
            return

        try:
            function_name = f.__name__
            url = f"{BASE_SERVER_URL}/{function_name}"

            data = dict(zip(f.__code__.co_varnames, args))
            data.update(kwargs)
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=data, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Server error: {response.status_code}")

            response_data = response.json()
            if "error" in response_data:
                raise Exception(f"Server returned an error: {response_data['error']}")
            return response_data["result"]
        except ConnectionError as err:
            # TODO
            raise err

    return wrapper


@rpc_call
def get_lsp_bridge_port() -> int:
    """
    Retrieves the port number on which the LSP (Language Server Protocol) bridge is running.

    Returns:
        int: The port number of the LSP bridge.

    Note:
        This function is expected to interact with an environment variable or a service
        that provides the LSP bridge port. The actual implementation details are not
        provided here and should be handled appropriately in the production code.
    """
    pass


@rpc_call
def install_python_env(command_name: str, requirements_file: str) -> str:
    """
    Installs a Python environment with the specified requirements.

    :param command_name: The name of the command associated with the environment.
    :param requirements_file: The path to the requirements file.
    :return: A string representing the Python command to activate the environment
             or an empty string if unsuccessful.
    """
    pass


@rpc_call
def update_slash_commands():
    """
    Updates the slash commands for the DevChat application.

    :return: A boolean indicating if the update was successful.
    """
    pass


@rpc_call
def open_folder(folder: str):
    """
    Opens a folder in the IDE.

    :param folder: The path to the folder to open.
    :return: A boolean indicating if the folder was successfully opened.
    """
    pass


@rpc_call
def ide_language() -> str:
    """
    Retrieves the current language setting for the DevChat application.

    :return: A string representing the language code (e.g., 'en' for English,
             'zh' for Simplified Chinese).
    """
    pass


@rpc_call
def log_info(message: str):
    """
    Logs an informational message to the DevChat application's logger.

    :param message: The message to log.
    :return: A boolean indicating if the logging was successful.
    """
    pass


@rpc_call
def log_warn(message: str):
    """
    Logs a warning message to the DevChat application's logger.

    :param message: The message to log.
    :return: A boolean indicating if the logging was successful.
    """
    pass


@rpc_call
def log_error(message: str):
    """
    Logs an error message to the DevChat application's logger.

    :param message: The message to log.
    :return: A boolean indicating if the logging was successful.
    """
    pass


@rpc_call
def visible_lines() -> Dict:
    """
    Fetches the currently visible lines in the active text editor.

    This function simulates an RPC call to an interface that retrieves the visible text range
    from a code editor (such as Visual Studio Code). The actual implementation of the RPC call
    is not provided here.

    Returns:
        A dictionary with the following keys:
            - "filePath" (str): The file path of the document in the active text editor.
            - "visibleText" (str): The text that is currently visible in the active text editor.
            - "visibleRange" (list): A list containing two integers, the start and end line numbers
                                      of the visible text range in the active text editor.

        If there is no active text editor, the function returns:
            - "filePath" as an empty string.
            - "visibleText" as an empty string.
            - "visibleRange" as a list with two elements, both set to -1.

    Example return value:
        {
            "filePath": "/path/to/file.py",
            "visibleText": "def foo():\n    return 'bar'\n",
            "visibleRange": [10, 12]
        }

        or, if there is no active editor:

        {
            "filePath": "",
            "visibleText": "",
            "visibleRange": [-1, -1]
        }
    """
    pass


@rpc_call
def selected_lines() -> Dict:
    """
    Retrieves the currently selected lines from the active text editor.

    Returns:
        A dictionary with the following keys:
        - "filePath": str - The file path of the current document.
        - "selectedText": str - The text that is currently selected.
        - "selectedRange": list - A list containing the start line, start character,
                                  end line, and end character of the selection.
                                  The line numbers are 0-based.

    If no text editor is active or no text is selected, the function returns:
        - "filePath": ""
        - "selectedText": ""
        - "selectedRange": [-1, -1, -1, -1]

    Note:
        This function is a wrapper for an RPC interface and assumes that the
        underlying RPC call is properly implemented and handles the communication
        with the text editor (e.g., Visual Studio Code).
    """
    pass


@rpc_call
def document_symbols(abspath: str) -> list:
    """
    Retrieves a list of symbols defined in a document at the given absolute path.

    Parameters:
    - abspath (str): The absolute path to the document for which symbols are requested.

    Returns:
    - list: A list of symbol dictionaries. Each symbol dictionary contains the following keys:
        - 'name': The name of the symbol (str).
        - 'kind': The kind of the symbol (int), corresponding to the SymbolKind enum in the
                language server protocol.
        - 'detail': Optional detail for the symbol (str), such as the type of a function.
        - 'range': A dictionary representing the range of the symbol with keys 'start_line',
                   'start_col', 'end_line', 'end_col' (integers).
        - 'selectionRange': A dictionary representing the selection range of the symbol with keys
                      'start_line', 'start_col', 'end_line', 'end_col' (integers).
        - 'children': An optional list of child symbol dictionaries (recursively structured like
                      the parent symbol dictionary).
        - 'location': (Only for SymbolInformation) A dictionary with a 'uri' key for the document
                      URI (str) and a 'range' key as defined above.
        - 'containerName': (Only for SymbolInformation) The name of the container that holds the
                           symbol (str), such as the name of a class or a namespace.

    Example:
    [
        {
            'name': 'MyClass',
            'kind': 5,  # Corresponds to SymbolKind.Class
            'detail': 'class MyClass',
            'range': {'start_line': 1, 'start_col': 0, 'end_line': 10, 'end_col': 1},
            'selectionRange': {'start_line': 1, 'start_col': 6, 'end_line': 1, 'end_col': 13},
            'children': [
                {
                    'name': '__init__',
                    'kind': 11,  # Corresponds to SymbolKind.Constructor
                    'detail': 'def __init__(self, param1)',
                    'range': {'start_line': 2, 'start_col': 4, 'end_line': 4, 'end_col': 5},
                    'selectionRange':
                        {'start_line': 2, 'start_col': 8, 'end_line': 2, 'end_col': 16},
                    'children': []
                }
            ]
        },
        {
            'name': 'my_function',
            'kind': 12,  # Corresponds to SymbolKind.Function
            'location': {
                'uri': 'file:///path/to/file.py',
                'range': {'start_line': 12, 'start_col': 0, 'end_line': 15, 'end_col': 1}
            },
            'containerName': 'MyModule'
        }
    ]

    Note:
    This function is a placeholder for the actual implementation that would interact with an RPC
    (Remote Procedure Call) interface to retrieve document symbols. The 'kind' values correspond to
    the SymbolKind enum defined in the language server protocol and must be mapped to appropriate
    values in the actual implementation.
    """
    pass


@rpc_call
def workspace_symbols(query: str) -> list:
    """
    This function is a Python interface for the workspace_symbols RPC endpoint.
    It retrieves symbols from a workspace based on a given query string.

    :param query: A string representing the query to search for symbols in the workspace.
    :return: A list of symbol information objects. Each object typically contains
             information like the symbol's name, location, kind (e.g., class, function),
             and container name. The exact structure of these objects can be found
             by referring to the document_symbols interface definition.

    Note: The actual implementation of querying the symbols and converting them to
    plain objects is not included in this interface definition.
    """
    pass


@rpc_call
def find_definition(abspath: str, line: int, col: int) -> list:
    """
    This function is a Python interface for the RPC 'find_definition' method. It returns
        a list of locations or location links where the definition of a symbol is found in the code.

    Args:
        abspath (str): The absolute path to the file in which to find the definition.
        line (int): The line number (0-indexed) where the symbol is located.
        col (int): The column number (0-indexed) where the symbol is located.

    Returns:
        list: A list of dictionaries, each representing either a vscode.Location or
            vscode.LocationLink object. Each dictionary has one of the following
            structures:

        vscode.Location representation:
        {
            'uri': str,  # The URI of the file containing the definition.
            'range': {
                'start_line': int,  # The start line number of the definition range (0-indexed).
                'start_col': int,  # The start column number of the definition range (0-indexed).
                'end_line': int,  # The end line number of the definition range (0-indexed).
                'end_col': int,  # The end column number of the definition range (0-indexed).
            }
        }

        vscode.LocationLink representation:
        {
            'originSelectionRange': Optional[dict],
                # The range of the symbol being searched for (if available).
            'targetUri': str,  # The URI of the target file containing the definition.
            'targetRange': {
                'start_line': int,  # The start line number of the target range (0-indexed).
                'start_col': int,  # The start column number of the target range (0-indexed).
                'end_line': int,  # The end line number of the target range (0-indexed).
                'end_col': int,  # The end column number of the target range (0-indexed).
            },
            'targetSelectionRange': {
                'start_line': int,
                    # The start line number of the target selection range (0-indexed).
                'start_col': int,
                    # The start column number of the target selection range (0-indexed).
                'end_line': int,  # The end line number of the target selection range (0-indexed).
                'end_col': int,  # The end column number of the target selection range (0-indexed).
            }
        }

    Example return value:
        [
            # vscode.Location example
            {
                'uri': 'file:///path/to/definition.py',
                'range': {
                    'start_line': 10,
                    'start_col': 4,
                    'end_line': 10,
                    'end_col': 20,
                }
            },
            # vscode.LocationLink example
            {
                'originSelectionRange': {
                    'start_line': 8,
                    'start_col': 12,
                    'end_line': 8,
                    'end_col': 16,
                },
                'targetUri': 'file:///path/to/definition.py',
                'targetRange': {
                    'start_line': 10,
                    'start_col': 4,
                    'end_line': 10,
                    'end_col': 20,
                },
                'targetSelectionRange': {
                    'start_line': 10,
                    'start_col': 4,
                    'end_line': 10,
                    'end_col': 20,
                }
            }
        ]
    """
    pass


@rpc_call
def find_type_definition(abspath: str, line: int, col: int) -> dict:
    """
    This function is a Python interface for the find_type_definition RPC call.
    It is designed to find the type definition of a symbol at a given position in a file.

    :param abspath: The absolute path to the file containing the symbol.
    :param line: The line number (0-indexed) where the symbol is located.
    :param col: The column number (0-indexed) where the symbol is located.

    :return: A dictionary containing the type definition information.
             The structure of the returned dictionary should be similar to the one
             returned by the find_definition RPC interface.

    Note: The actual implementation of the communication with the RPC server is not included.
    """
    pass


@rpc_call
def find_declaration(abspath: str, line: int, col: int) -> dict:
    """
    This function is a Python interface for the find_declaration RPC call.

    :param abspath: The absolute path to the file in which the declaration is to be found.
    :param line: The line number (0-indexed) where the declaration search will start.
    :param col: The column number (0-indexed) where the declaration search will start.
    :return: A dictionary containing the declaration information. For the structure of the
             return value, refer to the documentation of the find_definition RPC interface.

    Note: The actual implementation of the RPC call is not provided here. This function is
          only a stub
    representing the interface.
    """
    pass


@rpc_call
def find_implementation(abspath: str, line: int, col: int) -> dict:
    """
    This function is a Python interface for the find_implementation RPC method.
    It is intended to find the implementation of a symbol in the code.

    :param abspath: The absolute path to the file containing the symbol.
    :param line: The line number (0-indexed) where the symbol is located.
    :param col: The column number (0-indexed) where the symbol is located.

    :return: A dictionary containing the result of the find_implementation operation.
             The structure of the returned dictionary should follow the format
             specified by the find_definition interface's return value.

    Note: The actual implementation of this function is not provided here.
          This is only the function signature with parameter and return type annotations.
    """
    pass


@rpc_call
def find_reference(abspath: str, line: int, col: int) -> dict:
    """
    Provides a Python interface for the find_reference RPC endpoint.

    :param abspath: The absolute path to the file containing the symbol.
    :param line: The line number in the file where the symbol is located.
    :param col: The column number in the file where the symbol is located.
    :return: A dictionary containing the references found. The structure of the return value
             is analogous to the one provided by the find_definition interface.

    Note: This function is a stub and does not contain actual implementation.
    """
    pass


@rpc_call
def diff_apply(filepath: str, content: str) -> bool:
    """
    Opens a diff view to visually see the specific changes in the code.

    Parameters:
    filepath (str): The path to the file for which the diff will be applied.
    content (str): The modified content to be compared with the original file content.

    Returns:
    bool: True if the diff view was successfully opened, False otherwise.
    """
    pass
