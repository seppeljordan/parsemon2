from copy import copy

from parsemon.error import ParsingFailed
from parsemon.stack import Stack, StackEmptyError
from parsemon.trampoline import Call, Result, with_trampoline


class ParserBind(object):
    def __init__(self):
        self.callbacks = Stack()

    def __copy__(self):
        newbind = ParserBind()
        newbind.callbacks = self.callbacks
        return newbind

    def get_bind(self, value):
        try:
            parser_generator = self.callbacks.top()
            next_parser_bind = copy(self)
            next_parser_bind.callbacks = self.callbacks.pop()
            return (parser_generator(value), next_parser_bind)
        except StackEmptyError:
            return (None, None)

    def add_binding(self, binding):
        newbind = copy(self)
        newbind.callbacks = self.callbacks.push(binding)
        return newbind

    def pass_result(self, value, rest):
        next_parser, next_bind = self.get_bind(value)
        if next_parser is None:
            return Result((value, rest))
        else:
            return Call(next_parser, rest, next_bind)


def trampoline_const(v):
    return lambda x: Result(v)


def const(v):
    return lambda x: None


def run_parser(p, input_string):
    parsing_result, rest = with_trampoline(p)(
        input_string,
        ParserBind()
    )
    if rest:
        raise Exception(
            'Parser did not consume all of the string, rest was `{rest}`'
            .format(
                rest=rest
            )
        )
    else:
        return parsing_result


def bind_parser(binding, old_parser):
    def parser(s, parser_bind):
        return Call(old_parser, s, parser_bind.add_binding(binding))
    return parser


def parse_string(string_to_parse):
    def parser(s, parser_bind):
        if s.startswith(string_to_parse):
            rest = s[len(string_to_parse):]
            return parser_bind.pass_result(string_to_parse, rest)
        else:
            raise ParsingFailed(
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


def map_parser(mapping, old_parser):
    return bind_parser(
        lambda x: unit(mapping(x)),
        old_parser
    )


def parse_choice(first_parser, second_parser):
    def parser(s, parser_bind):
        try:
            result, rest = with_trampoline(first_parser)(
                s, parser_bind
            )
        except ParsingFailed:
            result, rest = with_trampoline(second_parser)(
                s, parser_bind
            )
        return Result((result, rest))
    return parser


def parse_many(original_parser):
    def parser(s, parser_bind):
        accu = []
        rest = s
        while True:
            try:
                result, rest = with_trampoline(original_parser)(
                    rest, parser_bind
                )
                accu += [result]
            except ParsingFailed:
                break
        return Result((accu, rest))
    return parser

def parse_until(d):
    def parser(s, parser_bind):
        splits = s.split(d)
        value = splits[0]
        rest = s[len(value) + len(d):]
        return parser_bind.pass_result(value, rest)
    return parser
