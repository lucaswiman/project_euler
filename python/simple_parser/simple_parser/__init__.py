from collections import namedtuple

from pyrsistent import pset
from toolz import interleave


class Rule(object):
    def matches_at_position(self, string, position):
        """
        Returns a generator of matches in the string which start at position.
        """
        raise NotImplementedError

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        return Concatenation(self, other)

    def __or__(self, other):
        return Disjunction(self, other)

    def parse(self, string):
        """
        Returns an iterator of all parse trees of the string for the given rule.
        """
        for match in self.matches_at_position(string, 0, stack=pset()):
            if match.length == len(string):
                yield match

    def matches(self, string):
        return bool(next(self.parse(string), False))


class Node(namedtuple('Node', ('string', 'position', 'length', 'rule', 'children'))):
    def __new__(cls, string, position, length, rule=None, children=()):
        return super(Node, cls).__new__(cls, string, position, length, rule, children)

    def __str__(self):
        return self.string[self.position:self.position + self.length]


class Literal(Rule):
    __slots__ = ('literal', 'length')

    def __init__(self, literal):
        self.literal = literal
        self.length = len(literal)

    def __hash__(self):
        return hash(self.literal)

    def __eq__(self, other):
        return isinstance(other, Literal) and other.literal == self.literal

    def __repr__(self):
        return 'Literal(%r)' % self.literal

    def matches_at_position(self, string, position, stack=pset()):
        if string.startswith(self.literal, position):
            yield Node(string, position, self.length, rule=self)


Epsilon = Literal('')


class Concatenation(Rule):
    __slots__ = ('head', 'tail', '_hash')

    def __new__(cls, *args):
        if not args:
            return Epsilon
        elif len(args) == 1:
            return args[0]
        else:
            concat = super(Concatenation, cls).__new__(cls)
            concat.head = args[0]
            concat.tail = Concatenation(*args[1:])
            return concat

    def __eq__(self, other):
        return (
            isinstance(other, Concatenation) and
            self.head == other.head and
            self.tail == other.tail)

    def __hash__(self):
        if not hasattr(self, '_hash'):
            self._hash = hash((self.__class__, self.head, self.tail))
        return self._hash

    def __iter__(self):
        cur = self
        while isinstance(cur, Concatenation):
            yield cur.head
            cur = cur.tail
        yield cur

    def __repr__(self):
        return 'Concatenation(%s)' % ', '.join(map(repr, self))

    def __add__(self, other):
        if isinstance(other, Concatenation):
            return Concatenation(*(tuple(self) + tuple(other)))
        else:
            return Concatenation(*(tuple(self) + (other, )))

    def matches_at_position(self, string, position, stack=pset()):
        if (self, position) in stack:
            # Prevent infinite recursion for zero-length terminals
            return
        stack = stack.add((self, position))
        for match in self.head.matches_at_position(string, position, stack=stack):
            for tail_match in self.tail.matches_at_position(string, position + match.length, stack=stack):
                children = (match, ) + (tail_match.children if tail_match.children else (tail_match, ))
                yield Node(
                    string,
                    position,
                    length=match.length + tail_match.length,
                    children=children,
                    rule=self,
                )


class Disjunction(tuple, Rule):
    def __new__(cls, *args):
        disjuncts = []
        for arg in args:
            if isinstance(arg, Disjunction):
                disjuncts.extend(arg)
            else:
                disjuncts.append(arg)
        return super(Disjunction, cls).__new__(cls, disjuncts)

    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, super(Disjunction, self).__repr__())

    def __add__(self, other):
        return Rule.__add__(self, other)

    def __hash__(self):
        if not hasattr(self, '_hash'):
            self._hash = tuple.__hash__(self)
        return self._hash

    def __eq__(self, other):
        return isinstance(other, Disjunction) and tuple.__eq__(self, other)

    def matches_at_position(self, string, position, stack=pset()):
        # Do a breadth-first search over the set of matches.
        if (self, position) in stack:
            # Prevent infinite recursion for zero-length terminals
            return
        stack = stack.add((self, position))
        yield from interleave(
            disjunct.matches_at_position(string, position, stack=stack)
            for disjunct in self)


class Reference(Rule):
    __slots__ = ('name', 'namespace')
    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace

    def __repr__(self):
        return 'Reference<%r>' % self.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            isinstance(other, Reference) and
            self.name == other.name and
            self.namespace is other.namespace)

    def matches_at_position(self, string, position, stack=pset()):
        if (self, position) in stack:
            # Prevent infinite recursion for zero-length matches.
            return
        stack = stack.add((self, position))
        yield from self.namespace[self.name].matches_at_position(string, position, stack=stack)
