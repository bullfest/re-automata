from .AST import _Lexer, Regex, _parse_re


def from_string(s: str) -> Regex:
    lexer = _Lexer(s)
    return _parse_re(lexer)
