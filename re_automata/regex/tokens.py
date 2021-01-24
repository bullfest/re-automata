from typing import Optional

META_CHARACTERS = ("|", "*", "+", "?", "(", ")", "[", "]", ".", "$")


# Here for future reference
# tokens = [
#     # Literal matches
#     "+",
#     "*",
#     "?",
#     "|",
#     ".",
#     "$",
#     "(",
#     ")",
#     "[",
#     "[^",
#     "]",
#     # regexes
#     r".",
#     r"\\.",
#     r"-",
# ]


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
