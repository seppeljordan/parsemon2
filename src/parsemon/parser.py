from functools import reduce
from typing import Callable, TypeVar, Tuple

from parsemon.internals import Parser, ParserState
from parsemon.trampoline import Call, Trampoline

S = TypeVar('S')
T = TypeVar('T')
U = TypeVar('U')
ParserInput = TypeVar('ParserInput')


def bind(
        old_parser: Parser[S, ParserInput],
        binding: Callable[[S], Parser[T, ParserInput]]
) -> Parser[T, ParserInput]:
    '''Combine the result of a parser with second parser

    :param old_parser: First parser to apply
    :param binding: A function that returns a parser based on the result
        of old_parser
    '''
    def parser(s, parser_bind) -> Trampoline[Tuple[T, ParserInput]]:
        return Call(
            old_parser,
            s,
            parser_bind.add_binding(binding)
        )
    return Parser(parser)


def chain(
        first: Parser[S, U],
        second: Parser[T, U]
) -> Parser[T, U]:
    '''Combine to parsers and only use the result of the second parser

    :param first: a parser that consumes input, the result will be discarded
    :param second: a parser that is applied after first, the result of this
        parser will be returned by the resulting parser
    '''
    return bind(
        first,
        lambda _: second,
    )


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
        suffix_parser: Parser[U, T]=None
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
