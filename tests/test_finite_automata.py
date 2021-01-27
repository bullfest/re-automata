import pytest

from re_automata.finite_automata import nfa_from_string
from re_automata.finite_automata.transition_tree import _less_than
from re_automata.regex.AST import (
    Char,
    Range,
    AstConstant,
)


@pytest.mark.parametrize(
    "regex, states",
    (
        ("a", 2),
        (".", 2),
        ("$", 2),
        ("[abc]", 2),
        ("[^abc]", 2),
        ("(a)", 2),
        ("a*", 3),
        ("a+", 2),
        ("a?", 2),
        ("a|b", 6),
        ("ab", 4),
        ("19|20", 10),
    ),
)
def test_nr_states(regex, states):
    assert len(nfa_from_string(regex).states) == states


@pytest.mark.parametrize(
    "a,b",
    (
        (Char("a"), Char("b")),
        (AstConstant.epsilon, Char(chr(0))),
        (AstConstant.epsilon, Range(Char("a"), Char("c"))),
        (AstConstant.any, AstConstant.end_of_string),
        (AstConstant.any, AstConstant.epsilon),
        (AstConstant.end_of_string, AstConstant.epsilon),
        (Range(Char("a"), Char("f")), Range(Char("g"), Char("m"))),
    ),
)
def test_less_than(a, b):
    assert _less_than(a, b)


@pytest.mark.parametrize(
    "a,b",
    (
        (Char("a"), Char("a")),
        (AstConstant.epsilon, AstConstant.epsilon),
        (Range(Char("a"), Char("f")), Range(Char("a"), Char("f"))),
        (Range(Char("a"), Char("f")), Range(Char("f"), Char("m"))),
        (Range(Char("a"), Char("z")), Range(Char("f"), Char("m"))),
        (Range(Char("a"), Char("f")), Range(Char("f"), Char("m"))),
        (Range(Char("a"), Char("f")), Char("d")),
    ),
)
def test_ish_equal(a, b):
    """Equal in the sense that neither a < b or b < a.

    This does not necessarily mean that a == b
    """
    assert not _less_than(a, b)
    assert not _less_than(b, a)
