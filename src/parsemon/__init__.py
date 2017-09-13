from typing import Callable, TypeVar

from parsemon.error import NotEnoughInput, ParsingFailed
from parsemon.internals import ParserState, Parser
from parsemon.trampoline import Call, with_trampoline

S = TypeVar('S')
T = TypeVar('T')


def run_parser(
        p: Parser[T],
        input_string: str
) -> T:
    parsing_result, rest = with_trampoline(p)(
        input_string,
        ParserState(input_string, 0)
    )
    if rest:
        raise ParsingFailed(
            'Parser did not consume all of the string, rest was `{rest}`'
            .format(
                rest=rest
            )
        )
    else:
        return parsing_result


def bind(
        old_parser: Parser[S],
        binding: Callable[[S], Parser[T]]
) -> Parser[T]:
    def parser(s, parser_bind):
        return Call(
            old_parser,
            s,
            parser_bind.add_binding(binding)
        )
    return parser


def chain(
        first: Parser[S],
        second: Parser[T]
) -> Parser[T]:
    return bind(
        first,
        lambda _: second,
    )


def literal(string_to_parse: str) -> Parser[str]:
    def parser(s, parser_bind):
        expected_length = len(string_to_parse)
        if s.startswith(string_to_parse):
            rest = s[expected_length:]
            return parser_bind.pass_result(
                string_to_parse, rest, characters_consumed=expected_length
            )
        else:
            return parser_bind.parser_failed(
                'Expected string `{expected}`, but saw `{actual}`'.format(
                    expected=string_to_parse,
                    actual=s[:len(string_to_parse)],
                )
            )
    return parser


def unit(u: T) -> Parser[T]:
    def unit_parser(s, parser_bind):
        return parser_bind.pass_result(u, s, characters_consumed=0)
    return unit_parser


def fmap(
        mapping: Callable[[S], T],
        old_parser: Parser[S]
) -> Parser[T]:
    return bind(
        old_parser,
        lambda x: unit(mapping(x)),
    )


def choice(
        first_parser: Parser[T],
        second_parser: Parser[T]
) -> Parser[T]:
    def parser(s: str, parser_bind: ParserState):
        return Call(
            first_parser,
            s,
            parser_bind.add_choice(second_parser, s)
        )
    return parser


def many(original_parser):
    return choice(
        bind(
            original_parser,
            lambda first_result: fmap(
                lambda rest_result: [first_result] + rest_result,
                many(original_parser),
            ),
        ),
        unit([]),
    )


def many1(original_parser):
    return bind(
        original_parser,
        lambda first_result: fmap(
            lambda rest_result: [first_result] + rest_result,
            many(original_parser),
        )
    )


def until(d: str):
    def parser(s, parser_bind: ParserState):
        splits = s.split(d)
        value = splits[0]
        characters_consumed = len(value) + len(d)
        rest = s[characters_consumed:]
        return parser_bind.pass_result(
            value, rest, characters_consumed=characters_consumed
        )
    return parser


def none_of(chars: str):
    def parser(s, parser_bind):
        if not s:
            return parser_bind.parser_failed(
                ('Excpected character other than `{forbidden}` but stream was '
                 'empty.').format(
                     forbidden=chars
                 )
            )
        value = s[0]
        rest = s[1:]
        if value in chars:
            return parser_bind.parser_failed(
                ('Expected character other than `{forbidden}`, '
                 'but got `{actual}`').format(
                     forbidden=chars,
                     actual=value
                 )
            )
        else:
            return parser_bind.pass_result(value, rest, characters_consumed=1)
    return parser


def fail(msg):
    def parser(s, parser_bind):
        return parser_bind.parser_failed(msg)
    return parser


def character(n=1):
    def parser(s, bind):
        rest_length = len(s)
        if rest_length >= n:
            return bind.pass_result(
                s[:n], s[n:], characters_consumed=n
            )
        else:
            return bind.parser_failed(
                'Expected `{expected}` characters of input but got only '
                '`{actual}`.'.format(
                    expected=n,
                    actual=rest_length
                ),
                exception=NotEnoughInput,
            )
    return parser
