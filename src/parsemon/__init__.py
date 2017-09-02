from parsemon.error import NotEnoughInput, ParsingFailed

from parsemon.internals import ParserBind
from parsemon.trampoline import Call, with_trampoline


def run_parser(p, input_string):
    parsing_result, rest = with_trampoline(p)(
        input_string,
        ParserBind()
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


def bind(binding, old_parser):
    def parser(s, parser_bind):
        return Call(old_parser, s, parser_bind.add_binding(binding))
    return parser


def chain(first, second):
    return bind(
        lambda _: second,
        first,
    )


def literal(string_to_parse):
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


def unit(u):
    def unit_parser(s, parser_bind):
        return parser_bind.pass_result(u, s)
    return unit_parser


def fmap(mapping, old_parser):
    return bind(
        lambda x: unit(mapping(x)),
        old_parser
    )


def choice(first_parser, second_parser):
    def parser(s, parser_bind):
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
                    rest, ParserBind()
                )
                accu += [result]
            except ParsingFailed:
                break
        return parser_bind.pass_result(accu, rest)
    return parser


def until(d: str):
    def parser(s, parser_bind: ParserBind):
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
