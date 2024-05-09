import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from tools.file_util import retrieve_file_content

from lib.ide_service import Position, SymbolNode


def split_tokens(text: str) -> Dict[str, List[int]]:
    """
    Split a line of text into tokens.
    Return a dictionary of token -> character numbers.

    Not a perfect implementation, but may be enough for now.
    """
    matches = re.finditer(r"\b\w+\b", text)
    result = defaultdict(list)
    for match in matches:
        token = match.group()
        result[token].append(match.start())

    return result


def locate_symbol_by_name(
    symbol_name: str, abspath: str, line_numbers: Optional[List[int]] = None
) -> List[Position]:
    """
    Find the locations of the specified symbol in the specified file.
    Line and column numbers are 0-based.

    symbol_name: The name of the symbol to find.
    abspath: The absolute path to the file to search.
    line_numbers: The line numbers to search for the symbol.
                If None, search the entire file.

    return: a list of Position
    """
    line_set = set(line_numbers) if line_numbers else None

    positions: List[Position] = []
    with open(abspath, "r") as file:
        for i, line in enumerate(file):
            if line_set and i not in line_set:
                continue

            tokens = split_tokens(line)
            chars = tokens.get(symbol_name, [])
            for char in chars:
                positions.append(Position(line=i, character=char))

    return positions


def find_symbol_nodes(
    symbols: List[SymbolNode], name: Optional[str] = None, line: Optional[int] = None
) -> List[Tuple[SymbolNode, int]]:
    """
    Find the symbols with the specified name and line number.

    return: a list of tuples (symbol, depth)
    """
    assert name is not None or line is not None

    res = []
    stack = [(s, 0) for s in symbols]
    while stack:
        symbol, depth = stack.pop()
        flag = True
        if name and symbol.name != name:
            flag = False
        if line and symbol.range.start.line != line:
            flag = False

        if flag:
            res.append((symbol, depth))
        else:
            stack.extend((c, depth + 1) for c in reversed(symbol.children))

    return res


def get_symbol_content(
    symbol: SymbolNode,
    file_content: Optional[str] = None,
    abspath: Optional[str] = None,
) -> str:
    """
    Get the content of the symbol in the file.
    """
    if file_content is None and abspath is None:
        raise ValueError("Either file_content or abspath should be provided")

    if file_content is None:
        file_content = retrieve_file_content(abspath, None)

    lines = file_content.split("\n")

    content = lines[symbol.range.start.line : symbol.range.end.line]
    content.append(lines[symbol.range.end.line][: symbol.range.end.character])

    return "\n".join(content)
