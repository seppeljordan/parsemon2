"""Implement basic parsers that should be generally useful"""

from typing import Tuple

from .coroutine import do
from .internals import fmap, literal, try_parser
from .parser import chain, choice, choices, many, many1, one_of, unit


def concat(chars):
    """Concatenate a list of chars to a string"""
    return "".join(chars)


DIGITS = "0123456789"
DIGIT = one_of(DIGITS)
PARSE_DIGITS = fmap(concat, many1(DIGIT))


@do
def integer():
    """Parse an integer."""
    first = yield one_of("+-" + DIGITS)
    if first == "-":
        sign = -1
        first = yield DIGIT
    elif first == "+":
        sign = 1
        first = yield DIGIT
    else:
        sign = 1
    rest = yield fmap(concat, many(DIGIT))
    return sign * int(first + rest)


@do
def floating_point(delimiter: str = "."):
    """Parse a floating point number.

    :param delimiter: defaults to ., is expected token to seperate integer part
        from rational part
    """

    @do
    def without_integer_part():
        yield literal(delimiter)
        after_point = yield PARSE_DIGITS
        return "", after_point

    @do
    def without_rational_part():
        before_point = yield PARSE_DIGITS
        yield literal(delimiter)
        return before_point, ""

    @do
    def both_parts():
        before_point = yield PARSE_DIGITS
        yield literal(delimiter)
        after_point = yield PARSE_DIGITS
        return before_point, after_point

    def sign():
        return choices(
            literal("+"),
            literal("-"),
            unit("+"),  # default to + when no sign is detected
        )

    @do
    def float_without_e():
        signum = yield sign()
        before_point, after_point = yield choices(
            without_integer_part(),
            try_parser(both_parts()),
            without_rational_part(),
        )
        return signum, before_point, after_point

    def parse_exponent():
        return choice(chain(one_of("eE"), fmap(str, integer())), unit("0"))

    def int_to_signum(n: int) -> Tuple[str, str, str]:
        return ("+" if n >= 0 else "-", str(n), "")

    signum, before_point, after_point = yield choice(
        try_parser(float_without_e()), fmap(int_to_signum, integer())
    )

    exponent = yield parse_exponent()
    return float(
        "{signum}{before_point}.{after_point}E{exponent}".format(
            signum=signum,
            before_point=before_point,
            after_point=after_point,
            exponent=exponent,
        )
    )
