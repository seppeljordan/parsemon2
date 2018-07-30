from copy import copy
from typing import Callable, Generic, Tuple, TypeVar, Sized

from parsemon.error import ParsingFailed
from parsemon.sourcemap import (display_location, find_line_in_indices,
                                find_linebreak_indices)
from parsemon.stack import Stack, StackEmptyError
from parsemon.trampoline import Call, Result, Trampoline

T = TypeVar('T')
ParserResult = TypeVar('ParserResult')
ParserInput = TypeVar('ParserInput')


class Parser(Generic[ParserResult, ParserInput]):
    def __init__(
            self,
            function: Callable[
                [ParserInput, 'ParserState'],
                Trampoline[Tuple[ParserResult, ParserInput]]
            ]
    ) -> None:
        self.function = function

    def __call__(
            self,
            input_value: ParserInput,
            parser_state: 'ParserState'
    ) -> Trampoline[Tuple[ParserResult, ParserInput]]:
        return self.function(input_value, parser_state)


class ParserState(Generic[T, ParserResult]):
    def __init__(
            self,
            document: Sized,
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

    def has_binding(self):
        return not self.callbacks.empty()

    def get_bind(
            self,
            value: T
    ) -> Tuple[Parser[ParserResult, Sized], 'ParserState[T, ParserResult]']:
        parser_generator: Callable[[T], Parser[ParserResult, Sized]]
        parser_generator = self.callbacks.top()
        next_parser_bind = copy(self)
        next_parser_bind.callbacks = self.callbacks.pop()
        return (
            parser_generator(value),
            next_parser_bind
        )

    def add_binding(
            self,
            binding: Callable[[T], Parser[T, ParserInput]]
    ) -> 'ParserState[T, ParserResult]':
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

    def copy_error_messages_from(
            self,
            other: 'ParserState[T, ParserResult]'
    ) -> 'ParserState[T, ParserResult]':
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
            parser: Parser[ParserResult, str],
            rest: str
    ) -> 'ParserState[T, ParserResult]':
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
            rest: Sized,
            characters_consumed=None,
    ) -> Trampoline:
        if self.has_binding():
            next_parser: 'Parser[ParserResult, Sized]'
            next_bind: 'ParserState[T, ParserResult]'
            next_parser, next_bind = self.get_bind(value)
            if characters_consumed is None:
                new_location = len(self.document) - len(rest)
            else:
                new_location = self.location + characters_consumed
            return Call(
                next_parser,
                rest,
                next_bind.set_location(new_location)
            )
        else:
            return Result((value, rest))

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
