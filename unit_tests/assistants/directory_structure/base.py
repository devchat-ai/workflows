from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Optional

from tools.directory_viewer import mk_repo_file_criteria


class DirectoryStructureBase(ABC):
    def __init__(
        self,
        root_path: str,
        chat_language: Optional[str] = None,
    ) -> None:
        self._root_path = root_path

        self._chat_language = chat_language

    @property
    def root_path(self) -> str:
        return self._root_path

    @property
    def chat_language(self) -> Optional[str]:
        return self._chat_language

    def mk_repo_criteria(self) -> Callable[[Path], bool]:
        """
        Make a criteria function to check if a path should be included or not.
        """
        # checks if a path meets the basic criteria for a git repo
        #   - not a hidden file
        #   - is source code file
        #   - is tracked by the current git
        repo_criteria = mk_repo_file_criteria(self.root_path)

        return repo_criteria

    @abstractmethod
    def analyze(self, **kwargs) -> Any:
        pass
