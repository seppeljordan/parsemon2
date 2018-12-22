"""This module parses json to python"""

from parsemon.coroutine import do
from parsemon.parser import (chain, choice, choices, enclosed_by, fail, fmap,
                             literal, many, many1, none_of, one_of,
                             seperated_by, unit, whitespace)

whitespaces = many(whitespace)

escape_pairs = (
    ('b', '\b'),
    ('f', '\f'),
    ('n', '\n'),
    ('r', '\r'),
    ('t', '\t'),
    ('"', '"'),
    ('\\', '\\'),
)


@do
def repeat(parser, n):
    result = []
    while n > 0:
        result.append((yield parser))
        n -= 1
    return result


@do
def unicode_char():
    yield literal('u')
    digits = yield fmap(
        ''.join,
        repeat(one_of('0123456789abcdefABCDEF'), n=4)
    )
    return chr(int(digits, 16))


def escaped_from_pair(escape_sequence, translation):
    return chain(literal(escape_sequence), unit(translation))


regular_escapes = map(
    lambda pair: escaped_from_pair(*pair),
    escape_pairs
)
escaped_char = choices(
    unicode_char(),
    *regular_escapes,
)
escaped_char = chain(literal('\\'), escaped_char)


def json_string():
    @do
    def json_string_inner():
        accumulated = []
        done = False
        while not done:
            character, done = yield choice(
                fmap(
                    lambda parsed: (parsed, False),
                    choice(
                        escaped_char,
                        none_of('"'),
                    )
                ),
                unit(('', True))
            )
            accumulated += character
        return ''.join(accumulated)

    return enclosed_by(json_string_inner(), literal('"'))


DIGIT = one_of('0123456789')
ONENINE = one_of('123456789')


@do
def json_number():
    just_one_digit = DIGIT

    @do
    def multiple_digits():
        first = yield ONENINE
        rest = yield many1(DIGIT)
        return ''.join([first] + rest)

    @do
    def maybe_leading_zero(parser):
        sign = yield choice(
            literal('-'),
            unit(''),
        )
        return sign + (yield parser)

    integer_part = yield maybe_leading_zero(choice(
        multiple_digits(),
        just_one_digit,
    ))

    @do
    def fraction():
        fraction_digits = fmap(''.join, many1(DIGIT))
        return (yield literal('.')) + (yield fraction_digits)

    float_part = yield choice(
        fraction(),
        unit('')
    )

    @do
    def exponent():
        yield one_of('eE')
        sign = yield one_of('+-')
        digits = yield fmap(''.join, many1(DIGIT))
        return 'e' + sign + digits

    exponent_part = yield choice(
        exponent(),
        unit('')
    )

    if exponent_part or float_part:
        return float(integer_part + float_part + exponent_part)
    else:
        return int(integer_part)


@do
def json_bool():
    return (yield (
        fmap(lambda _: True, literal('true')) |
        fmap(lambda _: False, literal('false'))
    ))


@do
def json_null():
    yield literal('null')
    return None


@do
def json_list():
    values_seperator = chain(
        whitespaces,
        literal(','),
        whitespaces,
    )

    values = seperated_by(
        json_value(),
        values_seperator,
    )

    return (yield enclosed_by(
        values,
        chain(literal('['), whitespaces),
        chain(whitespaces, literal(']')),
    ))


@do
def json_object():

    @do
    def key_value_pair():
        key = yield json_string()
        yield whitespaces
        yield literal(':')
        yield whitespaces
        value = yield json_value()
        return (key, value)

    pair_seperator = chain(
        whitespaces,
        literal(','),
        whitespaces,
    )

    key_value_pairs = yield enclosed_by(
        seperated_by(
            key_value_pair(),
            pair_seperator,
        ),
        chain(literal('{'), whitespaces),
        chain(whitespaces, literal('}'))
    )

    results = dict()
    for key, value in key_value_pairs:
        results[key] = value
    return results


def json_value():
    return choices(
        json_number(),
        json_string(),
        json_null(),
        json_list(),
        json_object(),
        json_bool(),
    )


@do
def json_document():
    yield whitespaces
    doc = yield json_value()
    yield whitespaces
    return doc