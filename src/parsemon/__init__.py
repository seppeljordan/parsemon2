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
        ParserState()
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
        binding: Callable[[S], Parser[T]],
        old_parser: Parser[S]
) -> Parser[T]:
    def parser(s, parser_bind):
        return Call(old_parser, s, parser_bind.add_binding(binding))
    return parser


def chain(
        first: Parser[S],
        second: Parser[T]
) -> Parser[T]:
    return bind(
        lambda _: second,
        first,
    )


def literal(string_to_parse: str) -> Parser[str]:
    def parser(s, parser_bind):
        if s.startswith(string_to_parse):
            rest = s[len(string_to_parse):]
            return parser_bind.pass_result(string_to_parse, rest)
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
        return parser_bind.pass_result(u, s)
    return unit_parser


def fmap(
        mapping: Callable[[S], T],
        old_parser: Parser[S]
) -> Parser[T]:
    return bind(
        lambda x: unit(mapping(x)),
        old_parser
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
    def parser(s, parser_bind):
        accu = []
        rest = s
        while True:
            try:
                result, rest = with_trampoline(original_parser)(
                    rest, ParserState()
                )
                accu += [result]
            except ParsingFailed:
                break
        return parser_bind.pass_result(accu, rest)
    return parser


def until(d: str):
    def parser(s, parser_bind: ParserState):
        splits = s.split(d)
        value = splits[0]
        rest = s[len(value) + len(d):]
        return parser_bind.pass_result(value, rest)
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
            return parser_bind.pass_result(value, rest)
    return parser


def fail(msg):
    def parser(s, parser_bind):
        return parser_bind.parser_failed(msg)
    return parser


def character(n=1):
    def parser(s, bind):
        rest_length = len(s)
        if rest_length >= n:
            return bind.pass_result(s[:n], s[n:])
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
