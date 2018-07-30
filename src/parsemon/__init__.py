# flake8: noqa: F401
from typing import Callable, TypeVar, Sized

from .error import NotEnoughInput, ParsingFailed
from .internals import Parser, ParserState
from .parser import (bind, chain, choice, choices, enclosed_by,
                     fail, fmap, many, many1, seperated_by, unit)
from .trampoline import with_trampoline

S = TypeVar('S')
T = TypeVar('T')
U = TypeVar('U')


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


def character(n:int=1) -> Parser[str, str]:
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
