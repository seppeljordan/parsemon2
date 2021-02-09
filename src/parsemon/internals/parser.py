"""Contains the implementation of the parser monad.  This module is
not intended to be used from outside this library.
"""
from functools import partial

from parsemon.stream import StringStream
from parsemon.trampoline import Call, Result, with_trampoline


def bind(parser, binding):
    def _combined_parser(stream, continuation):
        def bind_continuation(progressed_stream, previous_parsing_result):
            if previous_parsing_result.is_failure():
                return Call(continuation, progressed_stream, previous_parsing_result)
            next_parser = binding(previous_parsing_result.value)
            return Call(
                next_parser,
                progressed_stream,
                continuation,
            )

        return Call(
            parser,
            stream,
            bind_continuation,
        )

    return _combined_parser


def choice_continuation(
    original_stream_length,
    original_continuation,
    other,
    stream,
    result_of_self,
):
    if result_of_self.is_failure():
        if len(stream) == original_stream_length:
            return Call(
                other,
                stream,
                lambda stream, result_of_other: (
                    Call(
                        original_continuation,
                        stream,
                        result_of_self + result_of_other,
                    )
                    if result_of_other.is_failure()
                    else Call(original_continuation, stream, result_of_other)
                ),
            )
    return Call(original_continuation, stream, result_of_self)


def choose_parser(parser, other):
    return change_continuation(
        parser,
        lambda old_stream, continuation, new_stream, parsing_result: choice_continuation(
            len(old_stream), continuation, other, new_stream, parsing_result
        ),
    )


def change_continuation(parser, mapping):
    def _choice_parser(stream, continuation):
        return Call(parser, stream, partial(mapping, stream, continuation))

    return _choice_parser


def run(parser, input_string, stream_implementation=StringStream):
    return with_trampoline(parser)(
        stream_implementation.from_string(input_string),
        lambda stream, x: Result(
            (
                stream,
                x,
            )
        ),
    )
