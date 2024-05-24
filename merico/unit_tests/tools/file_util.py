import os
import re
from pathlib import Path
from typing import Dict, List


def retrieve_file_content(file_path: str, root_path: str) -> str:
    """
    Retrieve the content of a file given its relative or absolute path.

    If a relative path is provided, it will be joined with the root_path to form an absolute path.

    Args:
        file_path (str): The relative or absolute path to the file.
        root_path (str): The root directory path to be used if file_path is a relative path.

    Returns:
        str: The content of the file.
    """
    if not os.path.isabs(file_path):
        file_path = os.path.join(root_path, file_path)

    with open(file_path, "r") as file:
        content = file.read()
    return content


def remove_duplicates(items: List[str]) -> List[str]:
    """
    Remove duplicate items from a list while preserving the order.
    """
    seen = set()
    res = []
    for i in items:
        if i in seen:
            continue
        res.append(i)
        seen.add(i)
    return res


def check_file_exists(file_path: str, root_path: str) -> bool:
    """
    Check if a file exists at the given path.

    Args:
        file_path (str): The relative or absolute path to the file.
        root_path (str): The root directory path to be used if file_path is a relative path.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if not os.path.isabs(file_path):
        file_path = os.path.join(root_path, file_path)
    return os.path.isfile(file_path)


def verify_file_list(file_list: List[str], root_path: str) -> List[str]:
    """
    Sometimes the file list given by LLM may contain:
      - duplicated files
      - files that don't exist

    This function prunes the file list to make it reliable.
    """
    # Remove duplicates
    file_list = remove_duplicates(file_list)

    # Remove files that don't exist
    file_list = [f for f in file_list if check_file_exists(f, root_path)]

    return file_list


def resolve_relative_path(file: str, path: str) -> str:
    """Resolve a relative path based on the current file's path.

    Args:
        file (str): The path to the current file.
        path (str): The path to resolve.

    Returns:
        str: The resolved path if the input path is relative, otherwise the original path.
    """
    # Only resolve the path if it's relative
    if path.startswith("./") or path.startswith("../"):
        # Get the directory of the current file
        file_dir = os.path.dirname(file)

        # Join the directory with the relative path
        resolved_path = os.path.join(file_dir, path)

        # Normalize the path (resolve "..", ".", etc.)
        resolved_path = os.path.normpath(resolved_path)

        return resolved_path

    # If the path is not relative, return it as is
    return path


def is_not_hidden(relpath: Path) -> bool:
    return not relpath.name.startswith(".")


def is_source_code(file_name: str, only_code=False) -> bool:
    """
    Check if a given file is a source code file based on its extension.

    Args:
        file_name (str): The name of the file to check.
        only_code (bool): if include md/yaml/json...

    Returns:
        bool: True if the file is a source code file, False otherwise.
    """
    # List of meaningful source code file extensions
    source_code_extensions = [
        ".py",  # Python
        ".java",  # Java
        ".c",  # C
        ".cpp",  # C++
        ".h",  # C header
        ".hpp",  # C++ header
        ".hh",  # C++ header
        ".js",  # JavaScript
        ".ts",  # TypeScript
        ".go",  # Go
        ".rs",  # Rust
        ".rb",  # Ruby
        ".cs",  # C#
        ".m",  # Objective-C
        ".swift",  # Swift
        ".php",  # PHP
        ".kt",  # Kotlin
        ".scala",  # Scala
        ".r",  # R
        ".pl",  # Perl
        ".lua",  # Lua
        ".groovy",  # Groovy
        ".dart",  # Dart
        ".sh",  # Bash
        ".bat",  # Batch file
        ".ipynb",  # Jupyter Notebook
    ]
    if not only_code:
        source_code_extensions.extend(
            [
                ".md",  # Markdown
                ".yaml",  # YAML
                ".yml",  # YAML
            ]
        )

    _, extension = os.path.splitext(file_name)

    return extension in source_code_extensions


DEFAULT_TEST_REGS = [r"^(.+/)*[Tt]ests?/"]  # C, C++, OBJC
TEST_PATH_PATTERNS: Dict[str, List[str]] = {
    "C": DEFAULT_TEST_REGS,
    "C++": DEFAULT_TEST_REGS,
    "Objective-C": DEFAULT_TEST_REGS,
    # Gradle https://docs.gradle.org/current/userguide/java_testing.html#sec:test_detection
    "Java": [r"^(.+/)*src/test/.*Tests?.java$"],
    # jest
    "JavaScript": [r"(.+/)*(__[Tt]ests__/.*|((.*\.)?(test|spec)))\.[jt]sx?$"],
    # pytest https://docs.pytest.org/en/stable/goodpractices.html#conventions-for-python-test-discovery
    "Python": [r"(.*_test|.*/?test_[^/]*)\.py$"],
    "Ruby": [r"^(.+/)*(spec/.*_spec.rb|test/.*_test.rb)$"],
    # golang, from `go help test`
    "Go": [r"^(.+/)*[^_\.][^/]*_test.go$"],
    "PHP": [r"^(.+/)*[Tt]ests?/(.+/)*([^/]*[Tt]ests?\.php|[Ff]ixtures?/(.+/)*.+\.php)"],
    "Kotlin": [r"^(.+/)*src/test/.*Tests?.kt$"],
    "C#": [r"^(.+/)[^/]+[Tt]ests?.cs$"],
    "Swift": [r"^(.+/)*[^/]*Tests?.swift"],
    "Scala": [r"^(.+/)*src/test/.*(scala|sc)"],
    "Dart": [r"^(.+/)*[Tt]ests?/(.+/)*[^/]*[Tt]ests?.dart"],
    "Lua": [r"^(.+/)*(specs?/.*_spec|tests?/(.*_test|test_[^/]*))\.lua$"],
}
LANG_TEST_REGS: Dict[str, List] = {
    k: [re.compile(r) for r in v] for k, v in TEST_PATH_PATTERNS.items()
}


def is_test_file(file_path: str) -> bool:
    """
    Check if a given file is a test file based on its path.

    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if the file is a test file, False otherwise.
    """
    for _, regs in LANG_TEST_REGS.items():
        for reg in regs:
            if reg.match(file_path):
                return True
    return False
