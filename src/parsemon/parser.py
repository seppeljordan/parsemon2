from functools import reduce
from typing import Callable, Sized, TypeVar, List

from attr import evolve
from parsemon.error import NotEnoughInput, ParsingFailed
from parsemon.internals import Parser, ParserState
from parsemon.trampoline import Call, with_trampoline

S = TypeVar('S')
T = TypeVar('T')
U = TypeVar('U')
ParserInput = TypeVar('ParserInput')
ParserResult = TypeVar('ParserResult')


def bind(
        old_parser: Parser[ParserResult, ParserInput],
        binding: Callable[[ParserResult], Parser[T, ParserInput]]
) -> Parser[T, ParserInput]:
    '''Combine the result of a parser with second parser

    :param old_parser: First parser to apply
    :param binding: A function that returns a parser based on the result
        of old_parser
    '''
    return evolve(  # type: ignore
        old_parser,
        function=lambda parser_input, parser_state: Call(
            old_parser.function,
            parser_input,
            parser_state.add_binding(binding)
        )
    )


def chain(
        first: Parser[S, U],
        second: Parser[T, U],
        *rest
) -> Parser[T, U]:
    '''Combine to parsers and only use the result of the second parser

    :param first: a parser that consumes input, the result will be discarded
    :param second: a parser that is applied after first, the result of this
        parser will be returned by the resulting parser
    '''
    def _chain(p1, p2):
        return bind(
            p1,
            lambda _: p2
        )
    first_and_second_parser_combined = _chain(first, second)
    return reduce(_chain, rest, first_and_second_parser_combined)


def unit(u: T) -> Parser[T, U]:
    '''A parser that consumes no input and returns ``u``'''
    def unit_parser(s, parser_bind):
        return parser_bind.pass_result(u, s, characters_consumed=0)
    return Parser(unit_parser)


def fmap(
        mapping: Callable[[S], T],
        old_parser: Parser[S, U]
) -> Parser[T, U]:
    '''Apply a function to the result of a parser

    :param mapping: a function that is applied to the result of
        ``old_parser``

    :param old_parser: a parser, its result is passed into ``mapping``

    '''
    return bind(
        old_parser,
        lambda x: unit(mapping(x)),
    )


def choice(
        first_parser: Parser[T, str],
        second_parser: Parser[T, str]
) -> Parser[T, str]:
    '''Try one parser and try a second one if the first one fails'''
    def parser(s: str, parser_bind: ParserState):
        return Call(
            first_parser,
            s,
            parser_bind.add_choice(second_parser, s)
        )
    return Parser(parser)


def choices(parser, *parsers):
    '''Try the given parsers one at a time until one succeeds'''
    return reduce(
        choice,
        [parser] + list(parsers)
    )


def many(original_parser):
    '''Apply a parser 0 or more times

    The resulting parser is greedy, which means that it will be
    applied as often as possible, which also includes 0 times.  Think
    of this as Kleene-Star.

    :param original_parser: this parser will be applied as often as
        possible by the resulting new parser

    '''
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
    '''Apply a parser 1 or more times

    The resulting parser is greedy, which means that it will be
    applied as often as possible.  Think of this as an equivalent to
    the '+' operator in regular expressions.

    original_parser -- this parser will be applied 1 or more times by the
        resulting parser

    '''
    return bind(
        original_parser,
        lambda first_result: fmap(
            lambda rest_result: [first_result] + rest_result,
            many(original_parser),
        )
    )


def fail(msg):
    """This parser always fails with the message passed as ``msg``."""
    def parser(s, parser_bind):
        return parser_bind.parser_failed(msg)
    return parser


def seperated_by(parser, seperator):
    """Apply the input parser as often as possible, where occurences are
    seperated by input that can be parsed by 'seperator'.

    This can be useful to parse lists with seperators in between.  The
    parser ``seperated_by(many(none_of(',')), literal(','))`` will
    parse the string ``1,2,3,4`` and return the list
    ``['1','2','3','4']``.
    """
    return choice(
        bind(
            parser,
            lambda first_result: fmap(
                lambda rest_results: [first_result] + rest_results,
                many(
                    chain(
                        seperator,
                        parser
                    )
                )
            )
        ),
        unit([])
    )


def enclosed_by(
        parser: Parser[S, T],
        prefix_parser: Parser[U, T],
        suffix_parser: Parser[U, T] = None
) -> Parser[S, T]:
    '''Parse a string enclosed by delimeters

    The parser ``enclosed_by(many(none_of('"')),literal('"'))`` will
    consume the string ``"example"`` and return the python string
    ``'example'``.
    '''
    actual_suffix_parser: Parser[U, T]
    actual_suffix_parser = (
        prefix_parser
        if suffix_parser is None
        else suffix_parser
    )
    return chain(
        prefix_parser,
        bind(
            parser,
            lambda parser_result: chain(
                actual_suffix_parser,
                unit(parser_result)
            )
        )
    )


def run_parser(
        p: Parser[T, Sized],
        input_string: Sized
) -> T:
    '''Parse string input_string with parser p'''
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


def character(n: int = 1) -> Parser[str, str]:
    """Parse exactly n characters, the default is 1."""
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
    return Parser(parser)


def none_of(chars: str) -> Parser[str, str]:
    """Parse any character except the ones in ``chars``

    This parser will fail if it finds a character that is in
    ``chars``.

    """
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
    return Parser(parser)


def one_of(
        expected: str
) -> Parser[str, str]:
    """Parse only characters contained in ``expected``."""
    def parser(s, state):
        if len(s) < 1:
            return state.parser_failed(
                'Expected one of {expected}, but found end of string'.format(
                    expected=repr(expected),
                )
            )
        elif s[0] in expected:
            return state.pass_result(s[0], s[1:], characters_consumed=1)
        else:
            return state.parser_failed(
                'Expected one of {expected}, but found {actual}'.format(
                    expected=repr(expected),
                    actual=repr(s[0]),
                )
            )
    return Parser(parser)


def until(d: str) -> Parser[str, str]:
    '''Parse the input until string ``d`` is found.

    The string ``d`` won't be consumed.  Returns the consumed input as
    a string.

    '''
    def parser(s, parser_bind: ParserState):
        splits = s.split(d)
        value = splits[0]
        characters_consumed = len(value) + len(d)
        rest = s[characters_consumed:]
        return parser_bind.pass_result(
            value, rest, characters_consumed=characters_consumed
        )
    return Parser(parser)


def literal(string_to_parse: str) -> Parser[str, str]:
    '''Parse a literal string and return it as a result'''
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
    return Parser(parser)


whitespace_unicode_characters_decimals: List[int] = [
    9,
    10,
    11,
    12,
    13,
    32,
    133,
    160,
    5760,
    8192,
    8193,
    8194,
    8195,
    8196,
    8197,
    8198,
    8199,
    8200,
    8201,
    8202,
    8232,
    8233,
    8239,
    8287,
    12288
]

whitespace = one_of(
    ''.join(map(chr, whitespace_unicode_characters_decimals))
)
