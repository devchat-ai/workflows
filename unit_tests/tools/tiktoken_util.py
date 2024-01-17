import tiktoken


def get_encoding(encoding_name: str):
    """
    Get a tiktoken encoding by name.
    """
    try:
        return tiktoken.get_encoding(encoding_name)
    except Exception:
        from tiktoken import registry
        from tiktoken.core import Encoding
        from tiktoken.registry import _find_constructors

        def _get_encoding(name: str):
            _find_constructors()
            constructor = registry.ENCODING_CONSTRUCTORS[name]
            return Encoding(**constructor(), use_pure_python=True)

        return _get_encoding(encoding_name)
