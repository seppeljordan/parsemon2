"""Contains the implementation of the parser monad.  This module is not intended
to be used from outside this library
"""
from functools import reduce

from attr import attrib, attrs, evolve

from .stream import CharacterStream
from .trampoline import Call, Result, with_trampoline


@attrs
class Success:
    value = attrib()
    stream = attrib()


@attrs
class Failure:
    message = attrib()
    stream = attrib()


@attrs
class Failures:
    failures = attrib()

    def __add__(self, other):
        return Failures(
            failures = self.failures + other.failures
        )


def failure(message, stream):
    return Failures([Failure(
        message=message,
        stream=stream,
    )])


@attrs
class Parser:
    function = attrib()

    def bind(self, binding):
        def function(stream, cont):
            def continuation(first_result):
                if isinstance(first_result, Failures):
                    return Call(cont,first_result)
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
        return Parser(function)

    def __or__(self, other):
        def parser(stream, cont):
            def continuation(first_result):
                if isinstance(first_result, Failures):
                    if len(first_result.failures[-1].stream) == len(stream):
                        return Call(
                            other.function,
                            stream,
                            lambda second_result: Call(
                                cont,
                                (
                                    first_result + second_result
                                    if isinstance(second_result, Failures)
                                    else second_result
                                )
                            ),
                        )
                return Call(cont, first_result)
            return Call(
                self.function,
                stream,
                continuation
            )
        return Parser(parser)

    def run(self, input_string):
        return with_trampoline(self.function)(
            CharacterStream.from_string(input_string),
            lambda x: Result(x),
        )


def look_ahead(parser):
    def function(stream, cont):
        def continuation(result):
            if isinstance(result, Failures):
                return Call(
                    cont,
                    result
                )
            else:
                return Call(
                    cont,
                    evolve(
                        result,
                        stream=stream
                    )
                )
        return Call(
            parser.function,
            stream,
            continuation
        )
    return Parser(function)


def try_parser(parser):
    def function(stream, cont):
        def continuation(result):
            if isinstance(result, Failures):
                modified_result = evolve(
                    result,
                    failures=list(map(
                        lambda failure: evolve(
                            failure,
                            stream=stream,
                        ),
                        result.failures,
                    ))
                )
                return Call(
                    cont,
                    modified_result,
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
    return Parser(function)


def unit(value):
    def parser(stream, cont):
        return Call(
            cont,
            Success(
                value=value,
                stream=stream
            )
        )
    return Parser(parser)


def fail(msg):
    """This parser always fails with the message passed as ``msg``."""
    def parser(stream, cont):
        return Call(
            cont,
            failure(
                message=msg,
                stream=stream
            )
        )
    return Parser(parser)


def character(n: int = 1):
    """Parse exactly n characters, the default is 1."""
    def parser(stream, cont):
        result = []
        for _ in range(0,n):
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
            Success(
                value=''.join(result),
                stream=stream
            )
        )
    return Parser(parser)


def literal(expected):
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
                        message='Expected {expected} but found {actual}.'.format(
                            expected=expected,
                            actual=''.join(result) + next_char
                        ),
                        stream=old_stream
                    )
                )
        return Call(
            cont,
            Success(
                value=''.join(result),
                stream=stream
            )
        )
    return Parser(parser)

def none_of(chars: str):
    """Parse any character except the ones in ``chars``

    This parser will fail if it finds a character that is in
    ``chars``.

    """
    def parser(stream, cont):
        if not stream:
            return Call(
                cont,
                failure(
                    message='Expected any char except `{forbidden}` but found end of string'.format(
                        forbidden=chars,
                    ),
                    stream=stream,
                )
            )
        if stream.next() not in chars:
            result, stream = stream.read()
            return Call(
                cont,
                Success(
                    value=result,
                    stream=stream
                )
            )
        else:
            return Call(
                cont,
                failure(
                    message='Expected anything except one of `{forbidden}` but found {actual}'.format(
                        forbidden=chars,
                        actual=stream.next()
                    ),
                    stream=stream
                )
            )
    return Parser(parser)


def one_of(
        expected: str
):
    """Parse only characters contained in ``expected``."""
    def parser(stream, cont):
        if not stream:
            return Call(
                cont,
                failure(
                    message='Expected on of `{expected}` but found end of string'.format(
                        expected=expected
                    ),
                    stream=stream
                )
            )
        if stream.next() in expected:
            result, stream = stream.read()
            return Call(
                cont,
                Success(
                    value=result,
                    stream=stream
                )
            )
        else:
            return Call(
                cont,
                failure(
                    message='Expected one of `{expected}` but found {actual}'.format(
                        expected=expected,
                        actual=stream.next(),
                    ),
                    stream=stream
                )
            )
    return Parser(parser)
