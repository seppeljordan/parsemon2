"""This module contains the basic building blocks for implementing parsers"""

from functools import reduce
from typing import Callable, List, Sized, TypeVar

from attr import evolve

from .coroutine import do
from .deque import Deque
from .error import NotEnoughInput, ParsingFailed
from .internals import (Failures, Parser, character, literal, look_ahead,
                        one_of, try_parser, unit)
from .sourcemap import (display_location, find_line_in_indices,
                        find_linebreak_indices)
from .trampoline import Call, with_trampoline

S = TypeVar('S')
T = TypeVar('T')
U = TypeVar('U')
ParserInput = TypeVar('ParserInput')
ParserResult = TypeVar('ParserResult')


NO_FURTHER_RESULT = object()
"""This is only intended for internal use.  We use NO_FURTHER_RESULT
to signal that a parser was not able to yield a result.  We could use
None here but then we would not be able to work with parsers that
would actually return None as a positive parsing result.
"""


def bind(
        old_parser,
        binding,
):
    '''Combine the result of a parser with second parser

    :param old_parser: First parser to apply
    :param binding: A function that returns a parser based on the result
        of old_parser
    '''
    return old_parser.bind(binding)

def chain(
        first,
        second,
        *rest
):
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


def fmap(
        mapping: Callable[[S], T],
        old_parser,
):
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
        first_parser,
        second_parser,
):
    '''Try one parser and try a second one if the first one fails

    This behaves the same way as ``first_parser | second_parser`` would.
    '''
    return first_parser | second_parser


def choices(parser, *parsers):
    '''Try the given parsers one at a time until one succeeds'''
    return reduce(
        choice,
        [parser] + list(parsers)
    )


@do
def many(original_parser):
    '''Apply a parser 0 or more times

    The resulting parser is greedy, which means that it will be
    applied as often as possible, which also includes 0 times.  Think
    of this as Kleene-Star.

    :param original_parser: this parser will be applied as often as
        possible by the resulting new parser

    '''
    results = []
    while True:
        current_result = yield choice(
            try_parser(original_parser),
            unit(NO_FURTHER_RESULT)
        )
        if current_result is NO_FURTHER_RESULT:
            break
        else:
            results.append(current_result)
    return results


@do
def many1(original_parser):
    '''Apply a parser 1 or more times

    The resulting parser is greedy, which means that it will be
    applied as often as possible.  Think of this as an equivalent to
    the '+' operator in regular expressions.

    original_parser -- this parser will be applied 1 or more times by the
        resulting parser

    '''
    return [(yield original_parser)] + (yield many(original_parser))


@do
def seperated_by(parser, seperator):
    """Apply the input parser as often as possible, where occurences are
    seperated by input that can be parsed by 'seperator'.

    This can be useful to parse lists with seperators in between.  The
    parser ``seperated_by(many(none_of(',')), literal(','))`` will
    parse the string ``1,2,3,4`` and return the list
    ``['1','2','3','4']``.
    """
    results = []
    first_elem = yield (try_parser(parser) | unit(NO_FURTHER_RESULT))
    if first_elem is NO_FURTHER_RESULT:
        return results
    rest_elems = yield many(chain(seperator, parser))
    return [first_elem] + rest_elems


@do
def enclosed_by(
        parser,
        prefix_parser,
        suffix_parser=None,
):
    '''Parse a string enclosed by delimeters

    The parser ``enclosed_by(many(none_of('"')),literal('"'))`` will
    consume the string ``"example"`` and return the python string
    ``'example'``.
    '''
    yield prefix_parser
    result = yield parser
    yield suffix_parser or prefix_parser
    return result


def run_parser(
        p,
        input_string: str,
) -> T:
    '''Parse string input_string with parser p'''
    total_length = len(input_string)
    def render_failure(failure):
        location = total_length - len(failure.stream)
        linebreaks = find_linebreak_indices(input_string)
        line = find_line_in_indices(location, linebreaks)
        if linebreaks:
            column = location - linebreaks[line - 2] - 1
        else:
            column = location
        return '{message} @ {location}'.format(
            message=failure.message,
            location=display_location(line,column)
        )
    result = p.run(input_string)
    if isinstance(result, Failures):
        final_message = ' OR '.join(map(
            render_failure,
            result.failures
        ))
        raise ParsingFailed(final_message)
    else:
        rest = result.stream
        if rest:
            raise NotEnoughInput(
                'Parser did not consume all of the string, rest was `{rest}`'
                .format(
                    rest=rest.to_string()
                )
            )
        return result.value


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
"""Parse any character that is classified as a whitespace character by unicode
standard.  That includes newline characters."""


@do
def until(delimiter):
    ending = object()

    @do
    def found_end():
        yield literal(delimiter)
        return ending

    result = []
    while True:
        parsing_result = yield choice(
            look_ahead(found_end()),
            character(),
        )
        if parsing_result is ending:
            return ''.join(result)
        result.append(parsing_result)
