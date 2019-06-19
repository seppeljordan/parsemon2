"""This module contains the basic building blocks for implementing parsers"""

from functools import reduce
from typing import List, TypeVar

from .coroutine import do
from .error import ParsingFailed
from .internals import one_of, try_parser, unit
from .result import Failure, parsing_result
from .sourcemap import (display_location, find_linebreak_indices,
                        find_location_in_indices)

T = TypeVar('T')


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
        stream_implementation=None,
) -> T:
    '''Parse string input_string with parser p'''
    def render_failure(failure):
        linebreaks = find_linebreak_indices(input_string)
        line, column = find_location_in_indices(failure.position, linebreaks)
        return '{message} @ {location}'.format(
            message=failure.message,
            location=display_location(line, column)
        )

    kwargs = {}
    if stream_implementation:
        kwargs['stream_implementation'] = stream_implementation
    stream, result = p.run(input_string, **kwargs)
    if result.is_failure():
        failures = (
            [result]
            if isinstance(result, Failure)
            else result.failures
        )
        final_message = ' OR '.join(map(
            render_failure,
            failures
        ))
        raise ParsingFailed(final_message)
    else:
        return parsing_result(
            value=result.value,
            remaining_input=stream.to_string()
        )


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
def until(x, y):
    delimiter_token = object()
    found_elements = []
    while True:
        result = yield choice(
            chain(y, unit(delimiter_token)),
            x
        )
        if result is delimiter_token:
            break
        else:
            found_elements.append(None)
    return tuple(found_elements)
