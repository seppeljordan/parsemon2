"""Contains the implementation of the parser monad.  This module is
not intended to be used from outside this library.
"""
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


def choose_parser(parser, other):
    def _choice_parser(stream, continuation):
        def _choice_continuation(progressed_stream, parser_result):
            def _error_message_continuation(final_stream, other_result):
                if other_result.is_failure():
                    final_result = parser_result + other_result
                else:
                    final_result = other_result
                return Call(
                    continuation,
                    final_stream,
                    final_result,
                )

            if parser_result.is_failure():
                return Call(
                    other,
                    progressed_stream,
                    _error_message_continuation,
                )
            else:
                return Call(
                    continuation,
                    progressed_stream,
                    parser_result,
                )

        return Call(
            parser,
            stream,
            _choice_continuation,
        )

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
