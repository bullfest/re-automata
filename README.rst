RE-Automata
===========
A library for nifty logic on a slightly simplified regex, implemented through automata.

Regex Grammar:
--------------
All regular expressions that follow this grammar are supported::

   *re       ::= or | simple
    or       ::= simple '|' re

   *word     ::= concat | basic
    concat   ::= basic simple

   *part     ::= kleene | plus | maybe | atom
    kleene   ::= atom "*"
    plus     ::= atom "+"
    maybe    ::= atom "?"

   *atom     ::= group | posset | negset | any | eos | char

    group    ::= '(' re ')'
    char     ::= 'non-meta-char' | '\' 'any-char'
    any      ::= '.'
    eos      ::= '$'
    posset   ::= '[' setitems ']'
    negset   ::= '[^' setitems ']'

   *setitems ::= setitem setitems | eps
   *setitem  ::= range | char
    range    ::= char '-' char




Rows marked with ``*`` do not have a corresponding class in Python

