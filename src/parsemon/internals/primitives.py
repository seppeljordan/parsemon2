from parsemon.extensions import result, trampoline


def look_ahead(parser):
    def _wrapped_parser(stream, continuation):
        reset_point = stream.get_reset_point()

        def _reset_stream(stream, parsing_result):
            if parsing_result.is_failure():
                reset_point.destroy()
            else:
                stream.reset_stream(reset_point)
            return trampoline.Call(
                continuation,
                stream,
                parsing_result,
            )

        return trampoline.Call(
            parser,
            stream,
            _reset_stream,
        )

    return _wrapped_parser


def try_parser(parser):
    def _wrapped_parser(stream, continuation):
        reset_point = stream.get_reset_point()

        def _reset_stream(progressed_stream, parsing_result):
            if parsing_result.is_failure():
                stream.reset_stream(reset_point)
            else:
                reset_point.destroy()
            return trampoline.Call(
                continuation,
                stream,
                parsing_result,
            )

        return trampoline.Call(
            parser,
            stream,
            _reset_stream,
        )

    return _wrapped_parser


def unit(value):
    def parser(stream, cont):
        return trampoline.Call(
            cont,
            stream,
            result.success(
                value=value,
            ),
        )

    return parser


def fail(msg):
    """This parser always fails with the message passed as ``msg``."""

    def parser(stream, cont):
        return trampoline.Call(
            cont, stream, result.failure(message=msg, position=stream.position())
        )

    return parser


def character(n: int = 1):
    """Parse exactly n characters, the default is 1."""

    def parser(stream, cont):
        results = []
        read_count = 0
        for _ in range(0, n):
            char_found = stream.read()
            if not char_found:
                break
            read_count += 1
            results.append(char_found)
        if read_count < n:
            return trampoline.Call(
                cont,
                stream,
                result.failure(
                    message="Expected character but found end of string",
                    position=stream.position(),
                ),
            )
        return trampoline.Call(
            cont,
            stream,
            result.success(
                value="".join(results),
            ),
        )

    return parser


def literal(expected):
    """Parses exactly the string given and nothing else.

    If the parser already fails on the first element, no input will be
    consumed.
    """

    def parser(stream, cont):
        for expected_char in expected:
            character_read = stream.next()
            if character_read is None:
                return trampoline.Call(
                    cont,
                    stream,
                    result.failure(
                        "Expected `{expected}` but found end of string".format(
                            expected=expected,
                        ),
                        position=stream.position(),
                    ),
                )
            if expected_char == character_read:
                stream.read()
            else:
                return trampoline.Call(
                    cont,
                    stream,
                    result.failure(
                        message=("Expected `{expected}` but found `{actual}`.").format(
                            expected=expected, actual=character_read
                        ),
                        position=stream.position(),
                    ),
                )
        return trampoline.Call(
            cont,
            stream,
            result.success(
                value=expected,
            ),
        )

    return parser


def none_of(chars: str):
    """Parse any character except the ones in ``chars``

    This parser will fail if it finds a character that is in
    ``chars``.

    """

    def parser(stream, cont):
        next_char = stream.next()
        if next_char is None:
            return trampoline.Call(
                cont,
                stream,
                result.failure(
                    message=" ".join(
                        [
                            "Expected any char except `{forbidden}` but found end"
                            "of string"
                        ]
                    ).format(
                        forbidden=chars,
                    ),
                    position=stream.position(),
                ),
            )
        if next_char not in chars:
            read_character = stream.read()
            return trampoline.Call(
                cont,
                stream,
                result.success(
                    value=read_character,
                ),
            )
        else:
            return trampoline.Call(
                cont,
                stream,
                result.failure(
                    message=" ".join(
                        [
                            "Expected anything except one of `{forbidden}` but"
                            "found {actual}"
                        ]
                    ).format(forbidden=chars, actual=stream.next()),
                    position=stream.position(),
                ),
            )

    return parser


def one_of(expected: str):
    """Parse only characters contained in ``expected``."""

    def parser(stream, cont):
        next_character = stream.next()
        if next_character is None:
            return trampoline.Call(
                cont,
                stream,
                result.failure(
                    message=(
                        "Expected on of `{expected}` but found end of string".format(
                            expected=expected
                        )
                    ),
                    position=stream.position(),
                ),
            )
        if next_character in expected:
            read_character = stream.read()
            return trampoline.Call(
                cont,
                stream,
                result.success(
                    value=read_character,
                ),
            )
        else:
            return trampoline.Call(
                cont,
                stream,
                result.failure(
                    message=("Expected one of `{expected}` but found {actual}").format(
                        expected=expected,
                        actual=stream.next(),
                    ),
                    position=stream.position(),
                ),
            )

    return parser


def fmap(mapping, parser):
    """Applies a function to the result of a given parser"""

    def new_parser(stream, continuation):
        return trampoline.Call(
            parser,
            stream,
            lambda resulting_stream, result: trampoline.Call(
                continuation, resulting_stream, result.map_value(mapping)
            ),
        )

    return new_parser


def end_of_file():
    """Returns a parser that only succeeds with a value of None if there
    would be no further input to consume"""

    def parser(stream, cont):
        if stream.next() is None:
            return trampoline.Call(
                cont,
                stream,
                result.success(
                    value=None,
                ),
            )
        else:
            return trampoline.Call(
                cont,
                stream,
                result.failure(
                    message="Expected end-of-file but found `{char}`".format(
                        char=stream.next(),
                    ),
                    position=stream.position(),
                ),
            )

    return parser
