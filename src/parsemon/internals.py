from copy import copy
from typing import Callable, Generic, Tuple, TypeVar

from parsemon.error import ParsingFailed
from parsemon.sourcemap import (display_location, find_line_in_indices,
                                find_linebreak_indices)
from parsemon.stack import Stack, StackEmptyError
from parsemon.trampoline import Call, Result, Trampoline

S = TypeVar('S')
T = TypeVar('T')

Parser = Callable[[str, 'ParserState'], Trampoline[Tuple[T, str]]]


class ParserState(Generic[T]):
    def __init__(
            self,
            document: str,
            location: int,
    ) -> None:
        self.callbacks = Stack()
        self.choices = Stack()
        self.error_messages = Stack()
        self.document = document
        self.location = location

    def __copy__(self):
        newbind = ParserState(self.document, self.location)
        newbind.callbacks = self.callbacks
        newbind.choices = self.choices
        newbind.error_messages = self.error_messages
        return newbind

    def set_location(self, new_location):
        new_state = copy(self)
        new_state.location = new_location
        return new_state

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
        return self.add_binding(pop_error_message)

    def pop_error_message(self):
        newbind = copy(self)
        newbind.error_messages = self.error_messages.pop()
        return newbind

    def push_error_message_generator(
            self,
            msg_generator: Callable[[], str]
    ):
        newbind = copy(self)
        newbind.error_messages = self.error_messages.push(msg_generator)
        return newbind

    def copy_error_messages_from(self, other):
        p = copy(self)
        for item in reversed(other.error_messages):
            p.push_error_message_generator(item)
        return p

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
                next_bind.set_location(len(self.document) - len(rest))
            )

    @property
    def current_location(self):
        def do_it():
            linebreaks = find_linebreak_indices(self.document)
            line = find_line_in_indices(self.location, linebreaks)
            if linebreaks:
                column = self.location - linebreaks[line - 2] - 1
            else:
                column = self.location
            return line, column

        if hasattr(self, "_current_location"):
            return self._current_location
        else:
            self._current_location = do_it()
            return self._current_location

    def parser_failed(self, msg, exception=ParsingFailed):
        def rendered_message():
            line, column = self.current_location
            return '{message} @ {location}'.format(
                message=msg,
                location=display_location(line=line, column=column)
            )
        if self.next_choice() is None:
            old_message_generators = self.get_error_messages()
            old_messages = list(map(lambda f: f(), old_message_generators))
            final_message = ' OR '.join(
                [rendered_message()] + old_messages
            )
            raise exception(final_message)
        else:
            next_parser, rest, next_bind = self.next_choice()
            return Call(
                next_parser,
                rest,
                (next_bind
                 .copy_error_messages_from(self)
                 .push_error_message_generator(rendered_message))
            )
