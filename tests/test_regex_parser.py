from re_automata.regex.AST import (
    from_string,
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


def test_kleene_star_char():
    assert from_string("a*") == Kleene(Char("a"))


def test_plus_char():
    assert from_string("a+") == Plus(Char("a"))


def test_maybe_char():
    assert from_string("a?") == Maybe(Char("a"))


def test_group_char():
    assert from_string("(a)") == Group(Char("a"))


def test_posset():
    assert from_string("[a]") == PosSet([Char("a")])
    assert from_string("[-]") == PosSet([Char("-")])
    assert from_string("[()]") == PosSet([Char("("), Char(")")])
    assert from_string("[a-z]") == PosSet([Range("a", "z")])
    assert from_string("[a^]") == PosSet([Char("a"), Char("^")])


def test_negset():
    assert from_string("[^a]") == NegSet([Char("a")])
    assert from_string("[^^]") == NegSet([Char("^")])
    assert from_string("[^-]") == NegSet([Char("-")])
    assert from_string("[^()]") == NegSet([Char("("), Char(")")])
    assert from_string("[^a-z]") == NegSet([Range("a", "z")])
