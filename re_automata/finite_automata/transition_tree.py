from __future__ import annotations

from typing import Optional, Set

from re_automata.finite_automata.automata import TransitionLabel, State
from re_automata.regex.AST import AstConstant, Char, Range


class LabelCollisionError(Exception):
    """Indicates that there's already a colliding label
    Possible colliding labels are:
    """

    def __init__(self, label: TransitionLabel, states: Set[State]):
        self.label = label
        self.states = states


class TransitionTreeNode:
    """An AVL-tree that's used to keep track of edges in automatas.

    Primarily exists to be able to handle ranges in a reasonable way.
    """

    def __init__(self, parent: Optional[TransitionTreeNode]):
        self.parent = parent

        self.label: Optional[TransitionLabel] = None
        self.states: Set[State] = set()
        self.left: Optional[TransitionTreeNode] = None
        self.right: Optional[TransitionTreeNode] = None
        self.height = 0

    def set(self, label: TransitionLabel, states: Set[State]):
        if self.label is not None:
            raise ValueError("This node already has a label set")

        self.label = label
        self.states = states
        self.height = 1
        self.left = TransitionTreeNode(self)
        self.right = TransitionTreeNode(self)

    @property
    def bf(self):
        if self.label is None:
            # This node is a leaf
            return 0

        return self.left.height - self.right.height


def _less_than(a: TransitionLabel, b: TransitionLabel) -> bool:
    """
    Some ordering on labels.
    Both are same type:
    * AstConstants are compared by value
    * Char are compared by character
    * Range a is smaller than Range b if a.end < b.start

    Different types:
    * AstConstant is smaller than all other labels.
    * Char c is smaller than Range a if c < a.start
    * Range a is smaller than Character c if a.end < c

    Note that not _less_than(a,b) and not _less_than(b,a) does not imply a == b
    """
    if isinstance(a, AstConstant) and isinstance(b, AstConstant):
        return a.value < b.value
    if isinstance(a, Char) and isinstance(b, Char):
        return a.s < b.s
    if isinstance(a, Range) and isinstance(b, Range):
        return a.end.s < b.start.s
    if isinstance(a, AstConstant):
        return True
    if isinstance(b, AstConstant):
        return False
    if isinstance(a, Range):
        return _less_than(a.end, b)
    if isinstance(b, Range):
        return _less_than(a, b.start)

    # Shouldn't happen
    raise NotImplementedError()


class TranistionTree:
    def __init__(self):
        self.root = TransitionTreeNode(parent=None)

    def add(self, label: TransitionLabel, states: Set[State]):
        if isinstance(label, Range) and label.start == label.end:
            # Just one char in range -> Simplify
            label = label.start
        self.root = self._insert(self.root, label, states)

    def remove(self, label: TransitionLabel):
        raise NotImplementedError()  # TODO

    def _insert(
        self, node: TransitionTreeNode, label: TransitionLabel, states: Set[State]
    ) -> TransitionTreeNode:
        if node.label is None:
            node.set(label, states)
            return node
        assert node.left
        assert node.right
        if _less_than(label, node.label):
            node.left = self._insert(
                node.left,
                label,
                states,
            )
            node.left.parent = node
        elif _less_than(node.label, label):
            node.right = self._insert(
                node.right,
                label,
                states,
            )
            node.right.parent = node
        else:
            if label == node.label:
                node.states |= states
                return node
            # TODO: Support complicated collisions
            raise LabelCollisionError(node.label, node.states)

        node.height = max(node.left.height, node.right.height) + 1
        return self._rebalance(node)

    def _rebalance(self, node: TransitionTreeNode) -> TransitionTreeNode:
        if abs(node.bf) < 2:
            return node
        assert node.left
        assert node.right
        if node.bf >= 2:
            if node.left.bf < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        else:
            if node.right.bf > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

    def _rotate_left(self, node: TransitionTreeNode) -> TransitionTreeNode:
        pivot = node.right
        assert pivot
        tmp = pivot.left
        assert tmp

        pivot.left = node
        pivot.parent = node.parent
        node.parent = pivot

        node.right = tmp
        tmp.parent = node

        assert node.left
        assert pivot.right
        node.height = max(node.left.height, node.right.height) + 1
        pivot.height = max(pivot.left.height, pivot.right.height) + 1
        return pivot

    def _rotate_right(self, node: TransitionTreeNode) -> TransitionTreeNode:
        pivot = node.left
        assert pivot
        tmp = pivot.right
        assert tmp

        pivot.right = node
        pivot.parent = node.parent
        node.parent = pivot

        node.left = tmp
        tmp.parent = node

        assert node.right
        assert pivot.left
        node.height = max(node.left.height, node.right.height) + 1
        pivot.height = max(pivot.left.height, pivot.right.height) + 1
        return pivot
