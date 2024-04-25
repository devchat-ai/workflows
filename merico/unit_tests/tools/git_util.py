import functools
import os
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, List

import pathspec

# NOTE: git-ignore pattern examples
# https://www.atlassian.com/git/tutorials/saving-changes/gitignore#git-ignore-patterns


def load_gitignore_spec_from_file(
    ignore_filepath: str,
) -> pathspec.GitIgnoreSpec:
    """
    Create a path spec for match git ignore patterns from a given .gitignore file.

    ignore_filepath: The absolute path to the .gitignore file.
    """
    ignore_patterns = [".git/"]  # Ignore .git directory first

    if os.path.exists(ignore_filepath):
        with open(ignore_filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    ignore_spec = pathspec.GitIgnoreSpec.from_lines(ignore_patterns)

    return ignore_spec


def load_submodule_spec_from_file(
    modules_filepath: str,
) -> pathspec.GitIgnoreSpec:
    """
    Create a path spec to match submodule dirs & files from a given .gitmodules file.

    modules_filepath: The absolute path to the .gitmodules file.
    """
    submodule_dirs = []

    if os.path.exists(modules_filepath):
        with open(modules_filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("path = "):
                    submodule_dirs.append(line[7:])
    spec = pathspec.GitIgnoreSpec.from_lines(submodule_dirs)
    return spec


def load_gitlfs_spec_from_file(
    attributes_filepath: str,
) -> pathspec.GitIgnoreSpec:
    """
    Create a path spec to match git-lfs files from a given .gitattributes file.
    """
    lfs_patterns = []
    if os.path.exists(attributes_filepath):
        with open(attributes_filepath, "r") as f:
            for line in f:
                line = line.strip()
                items = line.split()
                if "filter=lfs" in items:
                    lfs_patterns.append(items[0])

    spec = pathspec.GitIgnoreSpec.from_lines(lfs_patterns)
    return spec


def _is_path_of_interest(relpath: Path, skip_specs: List[Dict]) -> bool:
    """
    Check if the given relative path is of interest.

    relpath: The relative path to the repo_root.
    skip_specs: A list of path spec dict to skip.
                key: The relative prefix of the path spec.
                value: The path spec.
    """
    skip = False
    for spec_dict in skip_specs:
        if skip:
            break

        for rel_prefix, spec in spec_dict.items():
            prefix = "" if rel_prefix == "." else rel_prefix + "/"
            prefix = Path(prefix)
            subpath = None
            try:
                subpath = relpath.relative_to(prefix)
            except ValueError:
                pass

            if subpath is None:
                continue

            if spec.match_file(str(subpath)):
                skip = True
                break

    return not skip


def git_file_of_interest_filter(repo_path: str) -> Callable[[Path], bool]:
    """
    Return a function which checks if a given relative path is of interest
    based on the gitignore and submodule specifications in a git repo.
    """
    repo_root = Path(repo_path)

    # Load submodule spec
    submodule_specs: Dict[str, List[pathspec.GitIgnoreSpec]] = {
        ".": load_submodule_spec_from_file(str(repo_root / ".gitmodules"))
    }

    # Load git-lfs spec
    lfs_specs: Dict[str, List[pathspec.GitIgnoreSpec]] = {
        ".": load_gitlfs_spec_from_file(str(repo_root / ".gitattributes"))
    }

    # Load gitignore specs
    ignore_specs = defaultdict(list)

    # find all .gitignore files
    ignore_files = []
    for fp in repo_root.rglob(".gitignore"):
        ignore_files.append(fp)

    for ignore_file in ignore_files:
        relative_prefix = str(ignore_file.parent.relative_to(repo_root))

        ignore_specs[relative_prefix] = load_gitignore_spec_from_file(str(ignore_file))

    is_git_interest = functools.partial(
        _is_path_of_interest,
        skip_specs=[
            dict(ignore_specs),
            submodule_specs,
            lfs_specs,
        ],
    )

    return is_git_interest
