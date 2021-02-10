"""This module parses json to python"""

from .coroutine import do
from .internals import fail, fmap, literal, look_ahead, none_of, try_parser, unit
from .parser import (
    chain,
    choice,
    choices,
    enclosed_by,
    many,
    many1,
    one_of,
    repeat,
    seperated_by,
    whitespace,
)


def concat(parser):
    return fmap("".join, parser)


whitespaces = many(whitespace)

escape_pairs = (
    ("b", "\b"),
    ("f", "\f"),
    ("n", "\n"),
    ("r", "\r"),
    ("t", "\t"),
    ('"', '"'),
    ("\\", "\\"),
)


@do
def unicode_char():
    yield literal("u")
    digits = yield concat(repeat(one_of("0123456789abcdefABCDEF"), 4))
    return chr(int(digits, 16))


def escaped_from_pair(escape_sequence, translation):
    return chain(literal(escape_sequence), unit(translation))


regular_escapes = map(lambda pair: escaped_from_pair(*pair), escape_pairs)
escaped_char = choices(
    unicode_char(),
    *regular_escapes,
)
escaped_char = chain(literal("\\"), escaped_char)


def json_string():
    json_string_inner = concat(many(choice(escaped_char, none_of('"\\'))))
    return enclosed_by(json_string_inner, literal('"'))


DIGIT = one_of("0123456789")
ONE_TO_NINE = one_of("123456789")


@do
def json_number():
    @do
    def just_one_digit():
        digit = yield DIGIT
        if digit == "0":
            is_next_char_digit = yield choice(
                chain(look_ahead(DIGIT), unit(True)),
                unit(False),
            )
            if is_next_char_digit:
                yield fail("Found leading zero in json number")
        return digit

    @do
    def multiple_digits():
        first = yield ONE_TO_NINE
        rest = yield many1(DIGIT)
        return "".join([first] + rest)

    @do
    def maybe_sign(parser):
        sign = yield choice(
            literal("-"),
            unit(""),
        )
        return sign + (yield parser)

    integer_part = yield maybe_sign(
        choice(
            try_parser(multiple_digits()),
            just_one_digit(),
        )
    )

    @do
    def fraction():
        fraction_digits = concat(many1(DIGIT))
        return (yield literal(".")) + (yield fraction_digits)

    float_part = yield choice(try_parser(fraction()), unit(""))

    @do
    def exponent():
        yield one_of("eE")
        sign = yield choice(one_of("+-"), unit(""))
        digits = yield concat(many1(DIGIT))
        return "e" + sign + digits

    exponent_part = yield choice(exponent(), unit(""))

    if exponent_part or float_part:
        return float(integer_part + float_part + exponent_part)
    else:
        return int(integer_part)


@do
def json_bool():
    return (
        yield (
            choice(
                fmap(lambda _: True, literal("true")),
                fmap(lambda _: False, literal("false")),
            )
        )
    )


@do
def json_null():
    yield literal("null")
    return None


@do
def json_list():
    values_seperator = chain(
        whitespaces,
        literal(","),
        whitespaces,
    )

    values = seperated_by(
        json_value(),
        values_seperator,
    )

    return (
        yield enclosed_by(
            values,
            chain(literal("["), whitespaces),
            chain(whitespaces, literal("]")),
        )
    )


@do
def json_object():
    @do
    def key_value_pair():
        key = yield json_string()
        yield whitespaces
        yield literal(":")
        yield whitespaces
        value = yield json_value()
        return (key, value)

    pair_seperator = chain(
        whitespaces,
        literal(","),
        whitespaces,
    )

    key_value_pairs = yield enclosed_by(
        seperated_by(
            key_value_pair(),
            pair_seperator,
        ),
        chain(literal("{"), whitespaces),
        chain(whitespaces, literal("}")),
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
