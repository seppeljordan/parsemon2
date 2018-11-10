from functools import reduce

from .coroutine import do
from .parser import choice, choices, fmap, literal, many, many1, one_of, unit


def concat(chars):
    return ''.join(chars)


DIGITS = '0123456789'
DIGIT = one_of(DIGITS)
PARSE_DIGITS = fmap(concat, many1(DIGIT))


@do
def integer():
    """Parse an integer."""
    first = yield one_of('+-' + DIGITS)
    if first == '-':
        sign = -1
        first = yield DIGIT
    elif first == '+':
        sign = 1
        first = yield DIGIT
    else:
        sign = 1
    rest = yield fmap(concat, many(DIGIT))
    return sign * int(first + rest)


@do
def floating_point():
    """Parse a floating point number."""
    @do
    def without_integer_part():
        yield literal('.')
        after_point = yield PARSE_DIGITS
        return '', after_point

    @do
    def without_rational_part():
        before_point = yield PARSE_DIGITS
        yield literal('.')
        return before_point, ''

    @do
    def both_parts():
        before_point = yield PARSE_DIGITS
        yield literal('.')
        after_point = yield PARSE_DIGITS
        return before_point, after_point

    @do
    def sign():
        parsed = yield choices(
            literal('+'),
            literal('-'),
            unit('+') # default to + when no sign is detected
        )
        return parsed

    @do
    def actual_float():
        signum = yield sign()
        before_point, after_point = yield choices(
            both_parts(),
            without_integer_part(),
            without_rational_part(),
        )
        return float(''.join([
            signum,
            before_point,
            '.',
            after_point
        ]))

    result = yield choice(
        actual_float(),
        fmap(float, integer())
    )
    return result
