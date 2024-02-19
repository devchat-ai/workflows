import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Set

from assistants.recommend_test_context import get_recommended_symbols
from model import FuncToTest
from tools.symbol_util import (
    find_symbol_nodes,
    get_symbol_content,
    locate_symbol_by_name,
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from libs.ide_services import IDEService, Location, SymbolNode


def _extract_referenced_symbols_context(
    func_to_test: FuncToTest, symbols: List[SymbolNode], depth: int = 0
) -> Dict[str, List[str]]:
    """
    Extract context of the document symbols referenced in the function.
    Exclude the function itself and symbols whose depth is greater than the specified depth.
    """
    referenced_symbols_context = defaultdict(list)
    func_content = func_to_test.func_content
    referenced_symbols = []
    stack = [(s, 0) for s in symbols]

    while stack:
        s, d = stack.pop()
        if d > depth:
            continue

        if s.name == func_to_test.func_name:
            # Skip the function itself and its children
            continue

        if s.name in func_content:
            # Use simple string matching for now
            referenced_symbols.append(s)

        stack.extend((c, depth + 1) for c in reversed(s.children))

    # Get the content of the symbols
    for s in referenced_symbols:
        content = get_symbol_content(s, file_content=func_to_test.file_content)
        referenced_symbols_context[s.name].append(content)
    return referenced_symbols_context


def _find_children_symbols_type_def_context(func_to_test: FuncToTest, func_symbol: SymbolNode):
    """
    Find the type definitions of the symbols in the function.
    """
    type_defs: Dict[str, List[str]] = defaultdict(list)

    client = IDEService()
    abs_path = os.path.join(func_to_test.repo_root, func_to_test.file_path)

    type_def_locations: Dict[str, Set[Location]] = defaultdict(set)
    # find type definitions for symbols in the function
    stack = func_symbol.children[:]
    while stack:
        s = stack.pop()

        locations = client.find_type_def_locations(
            abs_path, s.range.start.line, s.range.start.character
        )
        for loc in locations:
            # check if loc.abspath is in func_to_test.repo_root
            if not loc.abspath.startswith(func_to_test.repo_root):
                # skip, not in the repo
                continue
            if loc.abspath == abs_path:
                # skip, the symbol is in the same file
                continue

            type_def_locations[s.name].add(loc)

        stack.extend(s.children)

    # Get the content of the type definitions
    for symbol_name, locations in type_def_locations.items():
        for loc in locations:
            symbols = client.get_document_symbols(loc.abspath)
            targets = find_symbol_nodes(symbols, line=loc.range.start.line)
            for t, _ in targets:
                content = get_symbol_content(t, abspath=loc.abspath)
                type_defs[symbol_name].append(content)

    return type_defs


def _extract_recommended_symbols_context(
    func_to_test: FuncToTest, symbol_names: List[str]
) -> Dict[str, List[str]]:
    """
    Extract context of the given symbol names.
    """
    abs_path = os.path.join(func_to_test.repo_root, func_to_test.file_path)
    client = IDEService()

    # symbol name -> a list of context content (source code)
    recommended_symbols: Dict[str, List[str]] = defaultdict(list)

    type_def_locations: Dict[str, Set[Location]] = {}

    for symbol_name in symbol_names:
        type_def_locs = set()
        # locate the symbol in the file
        positions = locate_symbol_by_name(symbol_name, abs_path)
        for pos in positions:
            locations = client.find_type_def_locations(abs_path, pos.line, pos.character)
            for loc in locations:
                # check if loc.abspath is in func_to_test.repo_root
                if not loc.abspath.startswith(func_to_test.repo_root):
                    # skip, not in the repo
                    continue

                type_def_locs.add(loc)
        type_def_locations[symbol_name] = type_def_locs

    # Get the content of the type definitions
    for symbol_name, locations in type_def_locations.items():
        for loc in locations:
            # NOTE: further improvement is needed to
            # get the symbol node of function with decorator in Python
            symbols = client.get_document_symbols(loc.abspath)
            targets = find_symbol_nodes(symbols, name=symbol_name, line=loc.range.start.line)

            for t, _ in targets:
                content = get_symbol_content(t, abspath=loc.abspath)
                recommended_symbols[symbol_name].append(content)

    return recommended_symbols


def find_symbol_context_by_static_analysis(
    func_to_test: FuncToTest, chat_language: str
) -> Dict[str, List[str]]:
    """
    Find the context of symbols in the function to test by static analysis.
    """
    abs_path = os.path.join(func_to_test.repo_root, func_to_test.file_path)
    client = IDEService()

    # symbol name -> a list of  context content (code)
    symbol_context: Dict[str, List[str]] = defaultdict(list)

    # Get all symbols in the file
    doc_symbols = client.get_document_symbols(abs_path)
    # Find the symbol of the function to test
    func_symbols = find_symbol_nodes(
        doc_symbols, name=func_to_test.func_name, line=func_to_test.func_start_line
    )
    if not func_symbols:
        return symbol_context

    func_symbol, func_depth = func_symbols[0]

    context_by_reference = _extract_referenced_symbols_context(
        func_to_test, doc_symbols, depth=func_depth
    )
    context_by_type_def = _find_children_symbols_type_def_context(func_to_test, func_symbol)

    symbol_context.update(context_by_reference)
    symbol_context.update(context_by_type_def)

    return symbol_context


def find_symbol_context_of_llm_recommendation(
    func_to_test: FuncToTest, known_context: Optional[List[str]] = None
) -> List[str]:
    """
    Find the context of symbols recommended by LLM.
    """
    recommended_symbols = get_recommended_symbols(func_to_test, known_context)

    recommended_context = _extract_recommended_symbols_context(func_to_test, recommended_symbols)

    return recommended_context
