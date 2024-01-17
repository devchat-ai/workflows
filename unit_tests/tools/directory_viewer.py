from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Callable, List, Optional

from tools.file_util import is_not_hidden, is_source_code
from tools.git_util import git_file_of_interest_filter


class DirectoryViewer(ABC):
    def __init__(
        self,
        root_path: str,
        criteria: Optional[Callable] = None,
    ):
        self.root_path = Path(root_path)
        self.criteria = criteria

        self._items = None
        self._max_depth = None

    @property
    def items(self) -> List[Path]:
        """
        Get all items that pass the criteria under the root path.
        """
        if self._items is not None:
            return self._items

        self._items = []
        # Also compute the max depth when getting items
        max_depth = 0
        for filepath in self.root_path.rglob("*"):
            relpath = filepath.relative_to(self.root_path)
            if self.criteria and not self.criteria(relpath):
                continue

            depth = len(relpath.parts)
            max_depth = depth if depth > max_depth else max_depth

            self._items.append(filepath)

        self._items.sort(key=lambda s: str(s).lower())
        self._max_depth = max_depth
        return self._items

    @property
    def max_depth(self) -> int:
        # trigger the computation of max_depth
        _ = self.items
        return self._max_depth

    @abstractmethod
    def visualize(
        self,
        depth: Optional[int] = None,
        page_size: Optional[int] = None,
        page: int = 0,
    ) -> str:
        pass


def mk_repo_file_criteria(repo_path: str) -> Callable[[Path], bool]:
    is_git_interest = git_file_of_interest_filter(repo_path)

    def criteria(filepath: Path) -> bool:
        return (
            is_not_hidden(filepath) and is_git_interest(filepath) and is_source_code(str(filepath))
        )

    return criteria


class ListViewer(DirectoryViewer):
    def _get_items_to_show(
        self,
        depth: Optional[int] = None,
        page_size: Optional[int] = None,
        page: int = 0,
    ):
        """
        Get items with depth to show on the page.

        depth: 1-based.
        page: 0-based.
        """
        # Get items whose depth is less than or equal to the given depth.
        items_ = (
            self.items
            if depth is None
            else [i for i in self.items if len(i.relative_to(self.root_path).parts) <= depth]
        )

        # Get items to show on the page if page size is given.
        items_ = items_ if page_size is None else items_[page * page_size : (page + 1) * page_size]

        return items_

    def visualize(
        self,
        depth: Optional[int] = None,
        page_size: Optional[int] = None,
        page: int = 0,
    ) -> str:
        """
        Visualize the directory structure with the given depth and page size.

        Args:
            depth: 1-based depth of the dir structure to show. If None, show the entire dir.
            page_size: The number of items to show on the page. if None, show all items.
            page: The page number to show. 0-based.
        """
        items_to_show = self._get_items_to_show(depth=depth, page_size=page_size, page=page)
        dir_files = defaultdict(list)
        for item in items_to_show:
            relpath = item.relative_to(self.root_path)

            if item.is_file():
                dir_path = relpath.parent
                dir_files[dir_path].append(relpath)
            elif item.is_dir():
                # add a key to indicate there is a dir
                dir_files[relpath]

        keys = sorted(list(dir_files.keys()))

        visualization = ""
        for k in keys:
            visualization += f"\n`{k}`:\n"
            for item in dir_files[k]:
                visualization += f"- `{item.name}`\n"

        return visualization


class TreeViewer(DirectoryViewer):
    pass
