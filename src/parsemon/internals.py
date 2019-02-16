"""Contains the implementation of the parser monad.  This module is
not intended to be used from outside this library.
"""
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

    def bind(self, binding):
        @self.from_function
        def parser(stream, cont):
            def continuation(first_result):
                if first_result.is_failure():
                    return Call(cont, first_result)
                other = binding(first_result.value)
                return Call(
                    other.function,
                    first_result.stream,
                    cont,
                )
            return Call(
                self.function,
                stream,
                continuation,
            )
        return parser

    @classmethod
    def choice_continuation(
            cls,
            original_stream_length,
            original_continuation,
            other
    ):
        def _cont(result_of_self):
            if result_of_self.is_failure():
                if (
                        len(result_of_self.last_stream()) ==
                        original_stream_length
                ):
                    return Call(
                        other.function,
                        result_of_self.last_stream(),
                        lambda result_of_other: (
                            Call(
                                original_continuation,
                                result_of_self + result_of_other
                            )
                            if result_of_other.is_failure()
                            else Call(
                                    original_continuation,
                                    result_of_other
                            )
                        )
                    )
            return Call(original_continuation, result_of_self)
        return _cont

    def __or__(self, other):
        def parser(stream, cont):
            original_input_length = len(stream)
            return Call(
                self.function,
                stream,
                self.choice_continuation(original_input_length, cont, other)
            )
        return Parser(parser)

    def run(self, input_string, stream_implementation=StringStream):
        return with_trampoline(self.function)(
            stream_implementation.from_string(input_string),
            lambda x: Result(x),
        )

    @classmethod
    def from_function(cls, function):
        return cls(function)


def look_ahead(parser):
    @Parser.from_function
    def function(stream, cont):
        def continuation(result):
            if result.is_failure():
                return Call(
                    cont,
                    result
                )
            else:
                return Call(
                    cont,
                    result.map_stream(lambda _: stream),
                )
        return Call(
            parser.function,
            stream,
            continuation
        )
    return function


def try_parser(parser):
    @Parser.from_function
    def function(stream, cont):
        def continuation(result):
            if result.is_failure():
                return Call(
                    cont,
                    result.map_stream(lambda _: stream),
                )
            else:
                return Call(
                    cont,
                    result,
                )
        return Call(
            parser.function,
            stream,
            continuation,
        )
    return function


def unit(value):
    @Parser.from_function
    def parser(stream, cont):
        return Call(
            cont,
            success(
                value=value,
                stream=stream
            )
        )
    return parser


def fail(msg):
    """This parser always fails with the message passed as ``msg``."""
    @Parser.from_function
    def parser(stream, cont):
        return Call(
            cont,
            failure(
                message=msg,
                stream=stream
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
                    failure(
                        message='Expected character but found end of string',
                        stream=stream,
                    )
                )
            char_found, stream = stream.read()
            result.append(char_found)
        return Call(
            cont,
            success(
                value=''.join(result),
                stream=stream
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
        result = []
        for expected_char in expected:
            old_stream = stream
            next_char, stream = stream.read()
            if next_char is None:
                return Call(
                    cont,
                    failure(
                        'Expected `{expected}` but found end of string'.format(
                            expected=expected,
                        ),
                        old_stream,
                    )
                )
            if expected_char == next_char:
                result.append(expected_char)
            else:
                return Call(
                    cont,
                    failure(
                        message=(
                            'Expected {expected} but found {actual}.'
                        ).format(
                            expected=expected,
                            actual=''.join(result) + next_char
                        ),
                        stream=old_stream
                    )
                )
        return Call(
            cont,
            success(
                value=''.join(result),
                stream=stream
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
                failure(
                    message=' '.join([
                        'Expected any char except `{forbidden}` but found end'
                        'of string'
                    ]).format(
                        forbidden=chars,
                    ),
                    stream=stream,
                )
            )
        if stream.next() not in chars:
            result, stream = stream.read()
            return Call(
                cont,
                success(
                    value=result,
                    stream=stream
                )
            )
        else:
            return Call(
                cont,
                failure(
                    message=' '.join([
                        'Expected anything except one of `{forbidden}` but'
                        'found {actual}'
                    ]).format(
                        forbidden=chars,
                        actual=stream.next()
                    ),
                    stream=stream
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
                failure(
                    message=(
                        'Expected on of `{expected}` but found end of string'
                        .format(
                            expected=expected
                        )
                    ),
                    stream=stream
                )
            )
        if stream.next() in expected:
            result, stream = stream.read()
            return Call(
                cont,
                success(
                    value=result,
                    stream=stream
                )
            )
        else:
            return Call(
                cont,
                failure(
                    message=(
                        'Expected one of `{expected}` but found {actual}'
                    ).format(
                        expected=expected,
                        actual=stream.next(),
                    ),
                    stream=stream
                )
            )
    return parser


def fmap(mapping, parser):
    """Applies a function to the result of a given parser"""
    @Parser.from_function
    def mapped_parser(stream, cont):
        def continuation(parsing_result):
            return Call(
                cont,
                parsing_result.map_value(mapping)
            )
        return Call(
            parser.function,
            stream,
            continuation,
        )
    return mapped_parser


def end_of_file():
    """Returns a parser that only succeeds with a value of None if there
    would be no further input to consume"""
    @Parser.from_function
    def parser(stream, cont):
        if stream.next() is None:
            return Call(
                cont,
                success(
                    value=None,
                    stream=stream,
                )
            )
        else:
            return Call(
                cont,
                failure(
                    message='Expected end-of-file but found `{char}`'.format(
                        char=stream.next(),
                    ),
                    stream=stream,
                )
            )

    return parser
