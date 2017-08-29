from parsemon.trampoline import Call, Result, with_trampoline


class ParserBind(object):
    def __init__(self, callback=None):
        self.callback = callback
        self.value_mapping = lambda x: Result(x)

    def get_bind(self, value):
        if self.callback is not None:
            return (self.callback)(value)
        else:
            return None

    def map_bind(self, mapping):
        newbind = ParserBind()
        newbind.callback = self.callback
        newbind.value_mapping = lambda x: Call(self.value_mapping, mapping(x))
        return newbind

    def map_value(self, value):
        return with_trampoline(self.value_mapping)(value)

    def pass_result(self, old_value, rest):
        value = self.map_value(old_value)
        next_parser = self.get_bind(value)
        if next_parser is None:
            return Result((value, rest))
        else:
            return Call(next_parser, rest, ParserBind())


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
        raise Exception('parser did not consume all of the string')
    else:
        return parsing_result


def parse_string(string_to_parse):
    def parser(s, parser_bind):
        if s.startswith(string_to_parse):
            rest = s[len(string_to_parse):]
            return parser_bind.pass_result(string_to_parse, rest)
        else:
            raise Exception("parse error")
    return parser


def unit(u):
    def unit_parser(s, parser_bind):
        return parser_bind.pass_result(u, s)
    return unit_parser


def map_parser(mapping, old_parser):
    def mapped_parser(s, parser_bind):
        return Call(old_parser, s, parser_bind.map_bind(mapping))
    return mapped_parser
