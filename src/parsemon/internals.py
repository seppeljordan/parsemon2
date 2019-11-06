"""Contains the implementation of the parser monad.  This module is
not intended to be used from outside this library.
"""
from functools import partial

from attr import attrib, attrs

from .result import failure, success
from .stream import StringStream
from .trampoline import Call, Result, with_trampoline


@attrs
class Parser:
    """Constructs a Parser object from a function.

    The passed function must be a higher-order function.  The expected
    parameters are a parsermon.stream.CharacterStream first and a continuation
    function second.

    The function argument: The funtion parameter is expected to be a
    Callable.  Arguments that will be passed to that callable will be
    a CharacterStream `stream` and a continuation function
    `continuation`.  The function is expected to return either a
    Success or a Failure object.  When you write your own parser you
    get can read from the stream argument.  The return object will
    contain the remainder of the stream.  This is how you represent
    the amount of characters that your parser consumed.  Theoratically
    you can even write to that stream, but the author of this document
    can not come up with a good reason to do so.  The second expected
    parameter of that function is a little bit tricky.  `continuation`
    is expected to be a function that takes in the result of your
    parser and transforms it into another result object.  You as the
    author of parser function are responsible to call the
    `continuation` function on your parsing result.

    If you plan to write your own parsing function, the author
    recommends to look at the parser functions supplied with the
    parsemon package.

    Also: Your parsing function must implement the
    `parsemon.trampoline` protocol.  This means that if you do tail
    calls you implement them by returning a `parsemon.trampoline.Call`
    object.  Use `parseon.trampoline.Value` to return a plain value
    without doing a tail call.
    """
    function = attrib()

    @classmethod
    def bind_continuation(
            cls,
            original_continuation,
            binding,
            stream,
            previous_parsing_result
    ):
        if previous_parsing_result.is_failure():
            return Call(original_continuation, stream, previous_parsing_result)
        next_parser = binding(previous_parsing_result.value)
        return Call(
            next_parser.function,
            stream,
            original_continuation,
        )

    def bind(self, binding):
        @self.from_function
        def parser(stream, continuation):
            return Call(
                self.function,
                stream,
                partial(self.bind_continuation, continuation, binding)
            )
        return parser

    @classmethod
    def choice_continuation(
            cls,
            original_stream_length,
            original_continuation,
            other,
            stream,
            result_of_self,
    ):
        if result_of_self.is_failure():
            if (
                    len(stream) ==
                    original_stream_length
            ):
                return Call(
                    other.function,
                    stream,
                    lambda stream, result_of_other: (
                        Call(
                            original_continuation,
                            stream,
                            result_of_self + result_of_other
                        )
                        if result_of_other.is_failure()
                        else Call(
                                original_continuation,
                                stream,
                                result_of_other
                        )
                    )
                )
        return Call(original_continuation, stream, result_of_self)

    def __or__(self, other):
        return self.change_continuation(
            lambda old_stream, continuation, new_stream, parsing_result:
            self.choice_continuation(
                len(old_stream),
                continuation,
                other,
                new_stream,
                parsing_result
            )
        )

    def run(self, input_string, stream_implementation=StringStream):
        return with_trampoline(self.function)(
            stream_implementation.from_string(input_string),
            lambda stream, x: Result((
                stream,
                x,
            )),
        )

    @classmethod
    def from_function(cls, function):
        return cls(function)

    def change_continuation(self, mapping):
        @self.from_function
        def parser(stream, continuation):
            return Call(
                self.function,
                stream,
                partial(mapping, stream, continuation)
            )

        return parser


def look_ahead(parser):
    return parser.change_continuation(
        lambda old_stream, old_continuation, new_stream, parsing_result:
        Call(
            old_continuation,
            new_stream if parsing_result.is_failure() else old_stream,
            parsing_result,
        )
    )


def try_parser(parser):
    return parser.change_continuation(
        lambda old_stream, old_continuation, new_stream, parsing_result:
        Call(
            old_continuation,
            old_stream if parsing_result.is_failure() else new_stream,
            parsing_result,
        )
    )


def unit(value):
    @Parser.from_function
    def parser(stream, cont):
        return Call(
            cont,
            stream,
            success(
                value=value,
            )
        )
    return parser


def fail(msg):
    """This parser always fails with the message passed as ``msg``."""
    @Parser.from_function
    def parser(stream, cont):
        return Call(
            cont,
            stream,
            failure(
                message=msg,
                position=stream.position()
            )
        )
    return parser


def character(n: int = 1):
    """Parse exactly n characters, the default is 1."""
    @Parser.from_function
    def parser(stream, cont):
        result = []
        for _ in range(0, n):
            if not stream:
                return Call(
                    cont,
                    stream,
                    failure(
                        message='Expected character but found end of string',
                        position=stream.position(),
                    )
                )
            char_found, stream = stream.read()
            result.append(char_found)
        return Call(
            cont,
            stream,
            success(
                value=''.join(result),
            )
        )
    return parser


def literal(expected):
    """Parses exactly the string given and nothing else.

    If the parser already fails on the first element, no input will be
    consumed.
    """
    @Parser.from_function
    def parser(stream, cont):
        for expected_char in expected:
            character_read = stream.next()
            if character_read is None:
                return Call(
                    cont,
                    stream,
                    failure(
                        'Expected `{expected}` but found end of string'.format(
                            expected=expected,
                        ),
                        position=stream.position(),
                    )
                )
            if expected_char == character_read:
                stream = stream.read()[1]
            else:
                return Call(
                    cont,
                    stream,
                    failure(
                        message=(
                            'Expected `{expected}` but found `{actual}`.'
                        ).format(
                            expected=expected,
                            actual=character_read
                        ),
                        position=stream.position()
                    )
                )
        return Call(
            cont,
            stream,
            success(
                value=expected,
            )
        )
    return parser


def none_of(chars: str):
    """Parse any character except the ones in ``chars``

    This parser will fail if it finds a character that is in
    ``chars``.

    """
    @Parser.from_function
    def parser(stream, cont):
        if not stream:
            return Call(
                cont,
                stream,
                failure(
                    message=' '.join([
                        'Expected any char except `{forbidden}` but found end'
                        'of string'
                    ]).format(
                        forbidden=chars,
                    ),
                    position=stream.position(),
                )
            )
        if stream.next() not in chars:
            result, stream = stream.read()
            return Call(
                cont,
                stream,
                success(
                    value=result,
                )
            )
        else:
            return Call(
                cont,
                stream,
                failure(
                    message=' '.join([
                        'Expected anything except one of `{forbidden}` but'
                        'found {actual}'
                    ]).format(
                        forbidden=chars,
                        actual=stream.next()
                    ),
                    position=stream.position(),
                )
            )
    return parser


def one_of(
        expected: str
):
    """Parse only characters contained in ``expected``."""
    @Parser.from_function
    def parser(stream, cont):
        if not stream:
            return Call(
                cont,
                stream,
                failure(
                    message=(
                        'Expected on of `{expected}` but found end of string'
                        .format(
                            expected=expected
                        )
                    ),
                    position=stream.position()
                )
            )
        if stream.next() in expected:
            result, stream = stream.read()
            return Call(
                cont,
                stream,
                success(
                    value=result,
                )
            )
        else:
            return Call(
                cont,
                stream,
                failure(
                    message=(
                        'Expected one of `{expected}` but found {actual}'
                    ).format(
                        expected=expected,
                        actual=stream.next(),
                    ),
                    position=stream.position(),
                )
            )
    return parser


def fmap(mapping, parser):
    """Applies a function to the result of a given parser"""
    @Parser.from_function
    def new_parser(stream, continuation):
        return Call(
            parser.function,
            stream,
            lambda resulting_stream, result: Call(
                continuation,
                resulting_stream,
                result.map_value(mapping)
            )
        )
    return new_parser


def end_of_file():
    """Returns a parser that only succeeds with a value of None if there
    would be no further input to consume"""
    @Parser.from_function
    def parser(stream, cont):
        if stream.next() is None:
            return Call(
                cont,
                stream,
                success(
                    value=None,
                )
            )
        else:
            return Call(
                cont,
                stream,
                failure(
                    message='Expected end-of-file but found `{char}`'.format(
                        char=stream.next(),
                    ),
                    position=stream.position(),
                )
            )

    return parser
