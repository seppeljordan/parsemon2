from copy import copy
from typing import Callable, Generic, Tuple, TypeVar

from parsemon.error import ParsingFailed
from parsemon.stack import Stack, StackEmptyError
from parsemon.trampoline import Call, Result, Trampoline

S = TypeVar('S')
T = TypeVar('T')

Parser = Callable[[str, 'ParserState'], Trampoline[Tuple[T, str]]]


class ParserState(Generic[T]):
    def __init__(self):
        self.callbacks = Stack()
        self.choices = Stack()

    def __copy__(self):
        newbind = ParserState()
        newbind.callbacks = self.callbacks
        newbind.choices = self.choices
        return newbind

    def get_bind(
            self,
            value: T
    ) -> Tuple[Parser[S], 'ParserState[T]']:
        try:
            parser_generator = self.callbacks.top()
            next_parser_bind = copy(self)
            next_parser_bind.callbacks = self.callbacks.pop()
            return (parser_generator(value), next_parser_bind)
        except StackEmptyError:
            return (None, None)

    def add_binding(self, binding):
        newbind = copy(self)
        newbind.callbacks = self.callbacks.push(binding)
        return newbind

    def add_choice(
            self,
            parser: Parser[T],
            rest: str
    ) -> 'ParserState[T]':
        newbind = copy(self)
        newbind.choices = self.choices.push((parser, rest, self))
        return newbind

    def next_choice(self):
        try:
            return self.choices.top()
        except StackEmptyError:
            return None

    def pass_result(self, value: T, rest: str) -> Trampoline[str]:
        next_parser, next_bind = self.get_bind(value)
        if next_parser is None:
            return Result((value, rest))
        else:
            return Call(next_parser, rest, next_bind)

    def parser_failed(self, msg, exception=ParsingFailed):
        if self.next_choice() is None:
            raise exception(msg)
        else:
            next_parser, rest, next_bind = self.next_choice()
            return Call(next_parser, rest, next_bind)
