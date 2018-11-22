"""Contains the implementation of the parser monad.  This module is not intended
to be used from outside this library
"""
from typing import Any, Callable, Generic, Tuple, TypeVar

from attr import attrib, attrs, evolve

from .error import ParsingFailed
from .sourcemap import (display_location, find_line_in_indices,
                        find_linebreak_indices)
from .trampoline import Call, Result, Trampoline

CallbackInput = TypeVar('CallbackInput')
NextParserResult = TypeVar('NextParserResult')
ParserResult = TypeVar('ParserResult')
ParserInput = TypeVar('ParserInput')


@attrs
class Parser(Generic[ParserResult, ParserInput]):
    """Parser objects that can be consumed by ParserState"""
    function: Callable[
        [ParserInput, 'ParserState'],
        Trampoline[Tuple[ParserResult, ParserInput]]
    ] = attrib()

    def __call__(
            self,
            input_value: ParserInput,
            parser_state: 'ParserState[Any, ParserResult]'
    ) -> Trampoline[Tuple[ParserResult, ParserInput]]:
        return self.function(input_value, parser_state)

    def __or__(
            self,
            other
    ):
        def inner(s, parser_state):
            return Call(
                self,
                s,
                parser_state.add_choice(other, s)
            )
        return Parser(inner)


@attrs
class ParserState(Generic[CallbackInput, ParserResult]):
    """Class to handle the parsing process"""
    document: str = attrib()
    location: int = attrib()
    callbacks = attrib()
    choices = attrib()
    error_messages = attrib()

    @classmethod
    def create(cls, document, stack_implementation):
        return cls(
            document=document,
            location=0,
            callbacks=stack_implementation(),
            choices=stack_implementation(),
            error_messages=stack_implementation(),
        )


    def set_location(self, new_location):
        """Return new parsing status with document cursor set to given location.
        """
        return evolve(
            self,
            location=new_location
        )

    def has_binding(self):
        """Check if there are more parsing statements to process."""
        return not self.callbacks.empty()

    def get_bind(
            self,
            value: CallbackInput
    ) -> Tuple[
        Parser[ParserResult, str],
        'ParserState[CallbackInput, ParserResult]'
    ]:
        """Get next parser and updated parser state from previous parsing
        result.
        """
        return (
            self.callbacks.top()(value),
            evolve(
                self,
                callbacks=self.callbacks.pop()
            )
        )

    def add_binding(
            self,
            binding: Callable[
                [CallbackInput],
                Parser[NextParserResult, ParserInput]
            ]
    ) -> 'ParserState[CallbackInput, NextParserResult]':
        '''Add parsing continuation to the parser state'''
        return evolve(  # type: ignore
            self,
            callbacks=self.callbacks.push(binding)
        )

    def finally_remove_error_message(self):
        """Returns a new parser where all error messages are removed after
        succesful parsing.
        """
        def pop_error_message(value):
            return lambda rest, bindings: (
                bindings.pop_error_message().pass_result(
                    value=value,
                    characters_consumed=0
                )
            )
        return self.add_binding(pop_error_message)

    def pop_error_message(self):
        """Remove error message from message stack"""
        return evolve(
            self,
            error_messages=self.error_messages.pop()
        )

    def push_error_message_generator(
            self,
            msg_generator: Callable[[], str]
    ):
        '''Push new error message onto the message stack'''
        return evolve(
            self,
            error_messages=self.error_messages.append(msg_generator)
        )

    def copy_error_messages_from(
            self,
            other: 'ParserState[Any, ParserResult]'
    ) -> 'ParserState[CallbackInput, ParserResult]':
        """Copy error messages from other parser state"""
        return evolve(self, error_messages=other.error_messages)

    def get_error_messages(self):
        """Get all error messages stored in parser state."""
        return list(self.error_messages)

    def finally_remove_choice(self):
        """Returns new parser state where all choices are removed after
        succesfull parsing.
        """
        def pop_choice_parser(value):
            return lambda rest, bindings: (
                bindings.pop_choice().pass_result(
                    value=value,
                    characters_consumed=0,
                )
            )
        return self.add_binding(pop_choice_parser)

    def add_choice(
            self,
            parser: Parser[ParserResult, str],
            rest: str
    ) -> 'ParserState[CallbackInput, ParserResult]':
        '''Add a new alternative parser to parser state.'''
        return evolve(
            self,
            choices=self.choices.push((
                parser,
                rest,
                self.finally_remove_error_message()
            ))
        ).finally_remove_choice()

    def pop_choice(self):
        """Return a new parser state with next choice on stack removed"""
        return evolve(
            self,
            choices=self.choices.pop()
        )

    def next_choice(self):
        """Returns possibly the next choice given to the parser"""
        if self.choices.empty():
            return None
        return self.choices.top()

    def pass_result(
            self,
            value: CallbackInput,
            characters_consumed,
    ) -> Trampoline:
        """Signals that parsing was successful"""
        rest = self.document[self.location+characters_consumed:]
        if self.has_binding():
            next_parser: 'Parser[ParserResult, str]'
            next_bind: 'ParserState[CallbackInput, ParserResult]'

            next_parser, next_bind = self.get_bind(value)
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
        """Current location in the document that is to be parsed"""
        linebreaks = find_linebreak_indices(self.document)
        line = find_line_in_indices(self.location, linebreaks)
        if linebreaks:
            column = self.location - linebreaks[line - 2] - 1
        else:
            column = self.location
        return line, column

    def parser_failed(self, msg, exception=ParsingFailed):
        """Signals that the current parsing attempt failed.

        If possible, the we'll try again with alternatives that were provided.
        """
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
                old_messages + [rendered_message()]
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
