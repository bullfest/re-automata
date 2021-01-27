from __future__ import annotations

from typing import Set, Union, Tuple, List

from re_automata.regex.AST import (
    Regex,
    Char,
    Or,
    Concat,
    Kleene,
    Plus,
    Maybe,
    Group,
    PosSet,
    NegSet,
    AstConstant,
    Range,
)

TransitionLabel = Union[Char, Range, AstConstant]


def _nfa_step(regex: Regex) -> Automata:
    if isinstance(regex, (Char, AstConstant, PosSet, NegSet)):
        s1 = State()
        s2 = State()
        s1.add_transition(regex, s2)

        return Automata(
            states={s1, s2},
            start_state=s1,
            accepting_state=s2,
        )
    if isinstance(regex, Or):
        s1 = State()
        left_nfa = _nfa_step(regex.left)
        right_nfa = _nfa_step(regex.right)
        s2 = State()

        s1.add_transition(AstConstant.epsilon, left_nfa.start_state)
        s1.add_transition(AstConstant.epsilon, right_nfa.start_state)
        left_nfa.accepting_state.add_transition(AstConstant.epsilon, s2)
        right_nfa.accepting_state.add_transition(AstConstant.epsilon, s2)

        return Automata(
            states={s1, s2, *left_nfa.states, *right_nfa.states},
            start_state=s1,
            accepting_state=s2,
        )
    if isinstance(regex, Concat):
        left_nfa = _nfa_step(regex.left)
        right_nfa = _nfa_step(regex.right)
        left_nfa.accepting_state.add_transition(
            AstConstant.epsilon, right_nfa.start_state
        )
        return Automata(
            states=left_nfa.states | right_nfa.states,
            start_state=left_nfa.start_state,
            accepting_state=right_nfa.accepting_state,
        )
    if isinstance(regex, Kleene):
        # Extra node is added so that there isn't an epsilon-loop
        s = State()
        inner_nfa = _nfa_step(regex.r)
        s.add_transition(AstConstant.epsilon, inner_nfa.start_state)
        s.add_transition(AstConstant.epsilon, inner_nfa.accepting_state)
        inner_nfa.accepting_state.add_transition(
            AstConstant.epsilon, inner_nfa.start_state
        )
        return Automata(
            states=inner_nfa.states | {s},
            start_state=s,
            accepting_state=inner_nfa.accepting_state,
        )
    if isinstance(regex, Plus):
        inner_nfa = _nfa_step(regex.r)
        # Transition to redo inner
        inner_nfa.accepting_state.add_transition(
            AstConstant.epsilon, inner_nfa.start_state
        )
        return inner_nfa
    if isinstance(regex, Maybe):
        inner_nfa = _nfa_step(regex.r)
        # Transition to skip inner
        inner_nfa.start_state.add_transition(
            AstConstant.epsilon, inner_nfa.accepting_state
        )
        return inner_nfa
    if isinstance(regex, Group):
        return _nfa_step(regex.r)
    raise NotImplementedError()


def _split_labels(
    label1: TransitionLabel,
    states1: Set[State],
    label2: TransitionLabel,
    states2: Set[State],
) -> List[Tuple[TransitionLabel, Set[State]]]:
    # Either two partially overlapping Ranges or one Range that contains the Char
    if isinstance(label1, Range) and isinstance(label2, Range):
        label1, states1, label2, states2 = (
            (label1, states1, label2, states2)
            if (label1.start.s, label1.end.s) <= (label2.start.s, label2.end.s)
            else (label2, states2, label1, states1)
        )

        if label1.start == label2.start:
            assert label1.end.s < label2.end.s
            # ex: l1 = [a-f], l2 = [a-z]
            return [
                (label1, states1 | states2),
                (Range(Char(chr(ord(label1.end.s) + 1)), label2.end), states2),
            ]
        assert label1.start.s < label2.start.s
        if label1.end.s < label2.end.s:
            # ex: l1 = [a-d], l2 = [c-f]
            return [
                (Range(label1.start, Char(chr(ord(label2.start.s) - 1))), states1),
                (Range(label2.start, label1.end), states1 | states2),
                (Range(Char(chr(ord(label1.end.s) + 1)), label2.end), states2),
            ]
        if label1.end == label2.end:
            # ex: l1 = [a-z], l2 = [x-z]
            return [
                (Range(label1.start, Char(chr(ord(label2.start.s) - 1))), states1),
                (label2, states1 | states2),
            ]
        assert label1.end.s > label2.end.s
        # ex: l1 = [a-f], l2 = [c-d]
        return [
            (Range(label1.start, Char(chr(ord(label2.start.s) - 1))), states1),
            (label2, states1 | states2),
            (Range(Char(chr(ord(label2.end.s) + 1)), label1.end), states2),
        ]

    if isinstance(label1, Char):
        char_label = label1
        char_states = states1
    elif isinstance(label2, Char):
        char_label = label2
        char_states = states2
    else:
        assert False, "Bad logic"
    if isinstance(label1, Range):
        range_label = label1
        range_states = states1
    elif isinstance(label2, Range):
        range_label = label2
        range_states = states2
    else:
        assert False, "Bad logic"

    assert range_label.start.s <= char_label.s <= range_label.end.s

    labels: List[Tuple[TransitionLabel, Set[State]]] = []
    if range_label.start != char_label:
        labels.append(
            (Range(range_label.start, Char(chr(ord(char_label.s) - 1))), range_states)
        )
    labels.append((char_label, char_states | range_states))
    if range_label.end != char_label:
        labels.append(
            (Range(Char(chr(ord(char_label.s) + 1)), range_label.end), range_states)
        )
    return labels


class State:
    def __init__(self):
        from re_automata.finite_automata.transition_tree import TranistionTree

        self.transitions = TranistionTree()

    def add_transition(
        self, label: Union[TransitionLabel, PosSet, NegSet], target_state: State
    ):
        if isinstance(label, PosSet):
            for sublabel in label.items:
                self.add_transition(sublabel, target_state)
            return
        if isinstance(label, NegSet):
            raise NotImplementedError()  # TODO: ????
        from re_automata.finite_automata.transition_tree import LabelCollisionError

        try:
            self.transitions.add(label, {target_state})
        except LabelCollisionError as e:
            pairs = _split_labels(label, {target_state}, e.label, e.states)
            self.transitions.remove(e.label)
            for l, states in pairs:
                self.transitions.add(l, states)

            pass  # TODO: split the collision


class Automata:
    def __init__(
        self,
        states: Set[State],
        start_state: State,
        accepting_state: State,
    ):
        self.states = states
        self.start_state = start_state
        self.accepting_state = accepting_state

    def minimize(self):
        # TODO
        pass
