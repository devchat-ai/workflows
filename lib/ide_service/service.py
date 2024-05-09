from typing import List

from .idea_service import IdeaIDEService
from .rpc import rpc_method
from .types import Location, LocationWithText, SymbolNode
from .vscode_service import selected_range, visible_range


class IDEService:
    """
    Client for IDE service

    Usage:
    client = IDEService()
    res = client.ide_language()
    res = client.ide_logging("info", "some message")
    """

    def __init__(self):
        self._result = None

    @rpc_method
    def get_lsp_brige_port(self) -> str:
        """
        Get the LSP bridge port.

        :return: str
        """
        return self._result

    @rpc_method
    def install_python_env(self, command_name: str, requirements_file: str) -> str:
        """
        A method to install a Python environment with the provided command name
        and requirements file, returning python path installed.
        Command name is the name of the environment to be installed.
        """
        return self._result

    @rpc_method
    def update_slash_commands(self) -> bool:
        """
        Update the slash commands and return a boolean indicating the success of the operation.
        """
        return self._result

    @rpc_method
    def ide_language(self) -> str:
        """
        Returns the current IDE language setting for the user.
        - zh: Chinese
        - en: English
        """
        return self._result

    @rpc_method
    def ide_logging(self, level: str, message: str) -> bool:
        """
        Logs a message to the IDE.
        level: "info" | "warn" | "error" | "debug"
        """
        return self._result

    @rpc_method
    def get_document_symbols(self, abspath: str) -> List[SymbolNode]:
        """
        Retrieves the document symbols for a given file.

        Args:
            abspath: The absolute path to the file whose symbols are to be retrieved.

        Returns:
            A list of SymbolNode objects representing the symbols found in the document.
        """
        try:
            return [SymbolNode.parse_obj(node) for node in self._result]
        except Exception:
            # TODO: logging ide service error
            return []

    @rpc_method
    def find_type_def_locations(self, abspath: str, line: int, character: int) -> List[Location]:
        """
        Finds the location of type definitions within a file.

        Args:
            abspath: The absolute path to the file to be searched.
            line: The line number within the file to begin the search.
            character: The character position within the line to begin the search.

        Returns:
            A list of Location objects representing the locations of type definitions found.
        """
        try:
            return [Location.parse_obj(loc) for loc in self._result]
        except Exception:
            # TODO: logging ide service error
            return []

    @rpc_method
    def find_def_locations(self, abspath: str, line: int, character: int) -> List[Location]:
        try:
            return [Location.parse_obj(loc) for loc in self._result]
        except Exception:
            # TODO: logging ide service error
            return []

    @rpc_method
    def ide_name(self) -> str:
        """Returns the name of the IDE.

        This method is a remote procedure call (RPC) that fetches the name of the IDE being used.

        Returns:
            The name of the IDE as a string. For example, "vscode" or "pycharm".
        """
        return self._result

    @rpc_method
    def diff_apply(self, filepath, content) -> bool:
        """
        Applies a given diff to a file.

        This method uses the content provided to apply changes to the file
        specified by the filepath. It's an RPC method that achieves file synchronization
        by updating the local version of the file with the changes described in the
        content parameter.

        Args:
            filepath: The path to the file that needs to be updated.
            content: A string containing the new code that should be applied to the file.

        Returns:
            A boolean indicating if the diff was successfully applied.
        """
        return self._result

    def get_visible_range(self) -> LocationWithText:
        """
        Determines and returns the visible range of code in the current IDE.
        """
        # TODO: Implement vscode endpoint following the protocol in stead of using python wrapper
        if self.ide_name() == "vscode":
            return visible_range()
        return IdeaIDEService().get_visible_range()

    def get_selected_range(self) -> LocationWithText:
        """
        Retrieves the selected range of code in the current IDE.
        """
        # TODO: Implement vscode endpoint following the protocol in stead of using python wrapper
        if self.ide_name() == "vscode":
            return selected_range()
        return IdeaIDEService().get_selected_range()
