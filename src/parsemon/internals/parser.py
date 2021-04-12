"""Contains the implementation of the parser monad.  This module is
not intended to be used from outside of this library.
"""
from parsemon.extensions import trampoline
from parsemon.stream import StringStream


def bind(parser, binding):
    def _combined_parser(stream, continuation):
        def bind_continuation(progressed_stream, previous_parsing_result):
            if previous_parsing_result.is_failure():
                return trampoline.Call(
                    continuation, progressed_stream, previous_parsing_result
                )
            next_parser = binding(previous_parsing_result.value)
            return trampoline.Call(
                next_parser,
                progressed_stream,
                continuation,
            )

        return trampoline.Call(
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
                return trampoline.Call(
                    continuation,
                    final_stream,
                    final_result,
                )

            if parser_result.is_failure():
                return trampoline.Call(
                    other,
                    progressed_stream,
                    _error_message_continuation,
                )
            else:
                return trampoline.Call(
                    continuation,
                    progressed_stream,
                    parser_result,
                )

        return trampoline.Call(
            parser,
            stream,
            _choice_continuation,
        )

    return _choice_parser


def run(parser, input_string, stream_implementation=StringStream):
    return trampoline.with_trampoline(
        parser,
        stream_implementation.from_string(input_string),
        lambda stream, x: trampoline.Result(
            (
                stream,
                x,
            )
        ),
    )
