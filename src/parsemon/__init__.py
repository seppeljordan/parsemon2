from copy import copy

from parsemon.error import ParsingFailed
from parsemon.stack import Stack, StackEmptyError
from parsemon.trampoline import Call, Result, with_trampoline


class ParserBind(object):
    def __init__(self):
        self.callbacks = Stack()
        self.choices = Stack()

    def __copy__(self):
        newbind = ParserBind()
        newbind.callbacks = self.callbacks
        newbind.choices = self.choices
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

    def add_choice(self, parser, rest: str):
        newbind = copy(self)
        newbind.choices = self.choices.push((parser,rest,self))
        return newbind

    def next_choice(self):
        try:
            return self.choices.top()
        except StackEmptyError:
            return None

    def pass_result(self, value, rest: str):
        next_parser, next_bind = self.get_bind(value)
        if next_parser is None:
            return Result((value, rest))
        else:
            return Call(next_parser, rest, next_bind)

    def parser_failed(self, msg):
        if self.next_choice() is None:
            raise ParsingFailed(msg)
        else:
            next_parser, rest, next_bind = self.next_choice()
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
                    rest, parser_bind
                )
                accu += [result]
            except ParsingFailed:
                break
        return Result((accu, rest))
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
        value = s[0]
        rest = s[1:]
        if value in chars:
            return parser_bind.parser_failed(
                ('Expected character other that `{forbidden}`, '
                 'but got `{actual}`').format(
                     forbidden=chars,
                     actual=value
                 )
            )
        else:
            return parser_bind.pass_result(value,rest)
    return parser


def fail(msg):
    def parser(s, parser_bind):
        return parser_bind.parser_failed(msg)
    return parser


def character():
    def parser(s, bind):
        if s:
            return bind.pass_result(s[0], s[1:])
        else:
            return bind.parser_failed(
                'Excected character but there is nothing left to parse'
            )
    return parser
