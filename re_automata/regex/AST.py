from abc import ABCMeta
from typing import Optional, List, Union, Set


class _Lexer:
    def __init__(self, s: str):
        self.s = s
        self.i = 0

    def peek(self) -> Optional[str]:
        if self.i >= len(self.s):
            return None
        else:
            return self.s[self.i]

    def next(self) -> str:
        c = self.s[self.i]
        self.i += 1
        return c

    def consume(self, s: str):
        assert self.next() == s


class Regex(metaclass=ABCMeta):
    def __repr__(self):
        vars = {
            att_name: getattr(self, att_name)
            for att_name in dir(self)
            if not att_name.startswith("_")
        }

        var_args = ", ".join(f"{att}={repr(val)}" for att, val in vars.items())
        return f"{self.__class__.__name__}({var_args})"

    def __eq__(self, other):
        attrs = [attr for attr in dir(self) if not attr.startswith("_")]

        def attr_same(attr):
            return hasattr(self, attr) and getattr(self, attr) == getattr(other, attr)

        return isinstance(other, self.__class__) and all(map(attr_same, attrs))


class Or(Regex):
    def __init__(self, left: Regex, right: Regex):
        self.left = left
        self.right = right


class Concat(Regex):
    def __init__(self, left: Regex, right: Regex):
        self.left = left
        self.right = right


class Kleene(Regex):
    def __init__(self, r: Regex):
        self.r = r


class Plus(Regex):
    def __init__(self, r: Regex):
        self.r = r


class Maybe(Regex):
    def __init__(self, r: Regex):
        self.r = r


class Group(Regex):
    def __init__(self, r: Regex):
        self.r = r


class Char(Regex):
    def __init__(self, s: str):
        self.s = s


class Any(Regex):
    pass


class EndOfString(Regex):
    pass


class Range:
    def __init__(self, start: str, end: str):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return all(
            (
                isinstance(other, Range),
                self.start == other.start,
                self.end == other.end,
            )
        )


class PosSet(Regex):
    def __init__(self, items: List[Union[Char, Range]]):
        self.items = items


class NegSet(Regex):
    def __init__(self, items: List[Union[Char, Range]]):
        self.items = items


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
        return Any()
    if l.peek() == "$":
        l.consume("$")
        return EndOfString()
    return _parse_char(l)


def _parse_group(l: _Lexer) -> Group:
    l.consume("(")
    re = _parse_re(l)
    l.consume(")")
    return Group(re)


META_CHARACTERS = ("|", "*", "+", "?", "(", ")", "[", "]", ".", "$")


def _parse_char(l: _Lexer, in_set=False) -> Char:
    c = l.next()
    if c == "\\":
        if l.peek() is None:
            raise ValueError(
                "Unexpectedly reached end of string. Expected escaped character."
            )
        real_c = l.next()
        # TODO: handle \n and other special?
        return Char(real_c)
    if in_set:
        return Char(c)
    if c in META_CHARACTERS:
        raise ValueError(
            f'Found "{c}" at {l.i-1}. The character is not valid in this context'
        )
    return Char(c)


def _parse_set(l: _Lexer) -> Union[PosSet, NegSet]:
    l.consume("[")
    if l.peek() == "^":
        l.consume("^")
        return NegSet(_parse_items(l))
    return PosSet(_parse_items(l))


def _parse_items(l: _Lexer) -> List[Union[Char, Range]]:
    items = []
    while l.peek() != "]":
        c = l.next()
        if l.peek() == "-":
            l.consume("-")
            end = l.next()
            assert end != "]"
            items.append(Range(c, end))
            continue
        items.append(Char(c))
    l.consume("]")
    return items
