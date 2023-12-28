from dataclasses import dataclass
from typing import Optional
from chat.ask_codebase.tools.retrieve_file_content import retrieve_file_content


class TokenBudgetExceededException(Exception):
    pass


@dataclass
class FuncToTest:
    func_name: str
    repo_root: str
    file_path: str  # relative path to repo root
    func_start_line: int  # 0-based, inclusive
    func_end_line: int  # 0-based, inclusive
    # container_name: Optional[str] = None
    container_start_line: Optional[int] = None  # 0-based, inclusive
    container_end_line: Optional[int] = None  # 0-based, inclusive

    def __post_init__(self):
        assert self.func_start_line >= 0 and self.func_end_line >= 0

        # convert invalid line number to None
        if self.container_start_line is not None and self.container_start_line < 0:
            self.container_start_line = None
        if self.container_end_line is not None and self.container_end_line < 0:
            self.container_end_line = None

        self._func_content = None
        self._file_content = None
        self._container_content = None

    def __repr__(self) -> str:
        return f"{self.file_path}:L{self.func_start_line}:{self.func_name}"

    @property
    def file_content(self) -> str:
        if self._file_content is None:
            self._file_content = retrieve_file_content(self.file_path, self.repo_root)
        return self._file_content

    @property
    def func_content(self) -> str:
        if self._func_content is None:
            lines = self.file_content.split("\n")
            self._func_content = "\n".join(lines[self.func_start_line : self.func_end_line + 1])
        return self._func_content

    @property
    def container_content(self) -> Optional[str]:
        if self.container_start_line is None or self.container_end_line is None:
            return None

        if self._container_content is None:
            lines = self.file_content.split("\n")
            self._container_content = "\n".join(
                lines[self.container_start_line : self.container_end_line + 1]
            )
        return self._container_content
