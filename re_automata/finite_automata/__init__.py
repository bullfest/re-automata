from .automata import _nfa_step, Automata
from ..regex import from_string as regex_from_string


def dfa_from_string(regex: str) -> Automata:
    nfa = nfa_from_string(regex)
    return nfa.minimize()


def nfa_from_string(regex: str) -> Automata:
    re_ast = regex_from_string(regex)
    return _nfa_step(re_ast)
