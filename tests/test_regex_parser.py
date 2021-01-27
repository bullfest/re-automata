import pytest

from re_automata.regex import from_string
from re_automata.regex.AST import (
    Char,
    Concat,
    Or,
    Kleene,
    Plus,
    Maybe,
    Group,
    PosSet,
    Range,
    NegSet,
)


def test_char():
    assert from_string("\n") == Char("\n")
    assert from_string("a") == Char("a")
    assert from_string("b") == Char("b")
    assert from_string("-") == Char("-")
    assert from_string("\\a") == Char("a")
    assert from_string("\\$") == Char("$")
    assert from_string("\\\\") == Char("\\")


def test_concat_chars():
    assert from_string("aa") == Concat(Char("a"), Char("a"))
    assert from_string("aba") == Concat(Char("a"), Concat(Char("b"), Char("a")))


def test_or_chars():
    assert from_string("a|b") == Or(Char("a"), Char("b"))
    assert from_string("ab|01") == Or(from_string("ab"), from_string("01"))


def test_kleene_star_char():
    assert from_string("a*") == Kleene(Char("a"))


def test_plus_char():
    assert from_string("a+") == Plus(Char("a"))


def test_maybe_char():
    assert from_string("a?") == Maybe(Char("a"))


def test_group_char():
    assert from_string("(a)") == Group(Char("a"))


@pytest.mark.parametrize(
    "regex,expected",
    [
        ("[a]", PosSet([Char("a")])),
        ("[-]", PosSet([Char("-")])),
        ("[()]", PosSet([Char("("), Char(")")])),
        ("[a-z]", PosSet([Range(Char("a"), Char("z"))])),
        ("[a^]", PosSet([Char("a"), Char("^")])),
        ("[[]", PosSet([Char("[")])),
        ("[\\^]", PosSet([Char("^")])),
        ("[\\]]", PosSet([Char("]")])),
    ],
)
def test_posset(regex, expected):
    assert from_string(regex) == expected


@pytest.mark.parametrize(
    "regex,expected",
    [
        ("[^a]", NegSet([Char("a")])),
        ("[^-]", NegSet([Char("-")])),
        ("[^^]", NegSet([Char("^")])),
        ("[^()]", NegSet([Char("("), Char(")")])),
        ("[^a-z]", NegSet([Range(Char("a"), Char("z"))])),
        ("[^[]", NegSet([Char("[")])),
        ("[^\\]]", NegSet([Char("]")])),
    ],
)
def test_negset(regex, expected):
    assert from_string(regex) == expected
