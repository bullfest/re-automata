from typing import Union, List

from re_automata.regex.AST import (
    Char,
    Or,
    Concat,
    Kleene,
    Plus,
    Maybe,
    Group,
    PosSet,
    NegSet,
    Range,
    Regex,
    AstConstant,
)
from re_automata.regex.tokens import META_CHARACTERS, _Lexer


def from_string(s: str) -> Regex:
    lexer = _Lexer(s)
    return _parse_re(lexer)


def _parse_char(l: _Lexer, in_set=False) -> Char:
    c = l.next()
    if c == "\\":
        if l.peek() is None:
            raise ValueError(
                "Unexpectedly reached end of string. Expected escaped character."
            )
        real_c = l.next()
        return Char(real_c)
    if in_set:
        return Char(c)
    if c in META_CHARACTERS:
        raise ValueError(
            f'Found "{c}" at {l.i-1}. The character is not valid in this context'
        )
    return Char(c)


def _parse_re(l: _Lexer) -> Regex:
    word = _parse_word(l)
    if l.peek() is None or l.peek() == ")":
        return word
    if l.peek() != "|":
        raise ValueError(f'Expected "|" at {l.i}.')
    l.consume("|")
    return Or(word, _parse_re(l))


def _parse_word(l: _Lexer) -> Regex:
    part = _parse_part(l)
    if l.peek() in ("|", ")") or l.peek() is None:
        return part
    return Concat(part, _parse_word(l))


def _parse_part(l: _Lexer) -> Regex:
    atom = _parse_atom(l)
    if l.peek() == "*":
        l.consume("*")
        return Kleene(atom)
    if l.peek() == "+":
        l.consume("+")
        return Plus(atom)
    if l.peek() == "?":
        l.consume("?")
        return Maybe(atom)
    return atom


def _parse_atom(l: _Lexer) -> Regex:
    if l.peek() is None:
        raise ValueError("Reached end of string, expected more.")
    if l.peek() == "(":
        return _parse_group(l)
    if l.peek() == "[":
        return _parse_set(l)
    if l.peek() == ".":
        l.consume(".")
        return AstConstant.any
    if l.peek() == "$":
        l.consume("$")
        return AstConstant.end_of_string
    return _parse_char(l)


def _parse_group(l: _Lexer) -> Group:
    l.consume("(")
    re = _parse_re(l)
    l.consume(")")
    return Group(re)


def _parse_set(l: _Lexer) -> Union[PosSet, NegSet]:
    l.consume("[")
    if l.peek() == "^":
        l.consume("^")
        return NegSet(_parse_items(l))
    return PosSet(_parse_items(l))


def _parse_items(l: _Lexer) -> List[Union[Char, Range]]:
    items: List[Union[Char, Range]] = []
    while l.peek() != "]":
        c = _parse_char(l, in_set=True)
        if l.peek() == "-":
            l.consume("-")
            end = _parse_char(l, in_set=True)
            assert end != "]"
            items.append(Range(c, end))
            continue
        items.append(c)
    l.consume("]")
    return items
