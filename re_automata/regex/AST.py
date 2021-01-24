from abc import ABCMeta
from typing import List, Union


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
    def __init__(self, start: Char, end: Char):
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
