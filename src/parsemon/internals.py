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
        self.error_messages = Stack()

    def __copy__(self):
        newbind = ParserState()
        newbind.callbacks = self.callbacks
        newbind.choices = self.choices
        newbind.error_messages = self.error_messages
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

    def add_binding(
            self,
            binding: Callable[[T], Parser[T]]
    ):
        newbind = copy(self)
        newbind.callbacks = self.callbacks.push(binding)
        return newbind

    def finally_remove_error_message(self):
        def pop_error_message(value):
            return lambda rest, bindings: (
                bindings.pop_error_message().pass_result(value, rest)
            )
        self.add_binding(pop_error_message)

    def pop_error_message(self):
        newbind = copy(self)
        newbind.error_messages = self.error_messages.pop()
        return newbind

    def push_error_message(self, msg):
        newbind = copy(self)
        newbind.error_messages = self.error_messages.push(msg)
        return newbind

    def get_error_messages(self):
        return list(self.error_messages)

    def finally_remove_choice(self):
        def pop_choice_parser(value):
            return lambda rest, bindings: (
                bindings.pop_choice().pass_result(value, rest)
            )
        return self.add_binding(pop_choice_parser)

    def add_choice(
            self,
            parser: Parser[T],
            rest: str
    ) -> 'ParserState[T]':
        newbind = copy(self)
        newbind.choices = self.choices.push((
            parser,
            rest,
            self.finally_remove_error_message()
        ))
        return newbind.finally_remove_choice()

    def pop_choice(self):
        newbind = copy(self)
        newbind.choices = self.choices.pop()
        return newbind

    def next_choice(self):
        try:
            return self.choices.top()
        except StackEmptyError:
            return None

    def pass_result(
            self,
            value: T,
            rest: str
    ) -> Trampoline:
        next_parser, next_bind = self.get_bind(value)
        if next_parser is None:
            return Result((value, rest))
        else:
            return Call(
                next_parser,
                rest,
                next_bind
            )

    def parser_failed(self, msg, exception=ParsingFailed):
        if self.next_choice() is None:
            old_messages = self.get_error_messages()
            final_message = ' OR '.join(
                [msg] + old_messages
            )
            raise exception(final_message)
        else:
            next_parser, rest, next_bind = self.next_choice()
            if next_bind is None:
                next_bind_with_error_message = \
                    ParserState().push_error_message(msg)
            else:
                next_bind_with_error_message = \
                    next_bind.push_error_message(msg)
            return Call(
                next_parser,
                rest,
                next_bind_with_error_message
            )
