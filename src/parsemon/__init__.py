from parsemon.trampoline import Call, Result, with_trampoline

def trampoline_const(v):
    return lambda x: Result(v)


def const(v):
    return lambda x: None


def run_parser(p, input_string):
    parsing_result, rest = with_trampoline(p)(
        input_string,
        const(None)
    )
    if rest:
        raise Exception('parser did not consume all of the string')
    else:
        return parsing_result


def parse_string(string_to_parse):
    def parser(s,get_next_parser):
        if s.startswith(string_to_parse):
            rest = s[len(string_to_parse):]
            next_parser = get_next_parser(string_to_parse)
            if next_parser is None:
                return Result((string_to_parse, rest))
            else:
                return Call(next_parser, rest, const(None))
        else:
            raise Exception("parse error")
    return parser


def unit(u):
    def unit_parser(s, get_next_parser):
        next_parser = get_next_parser(u)
        if next_parser is None:
            return Result((u, s))
        else:
            return Call(next_parser, s, const(None))

    return unit_parser


def map_parser(mapping, old_parser):
    def mapped_parser(s, get_next_parser):

        def mapped_get_next_parser(unmapped_result):
            result = mapping(unmapped_result)
            next_parser = get_next_parser(result)
            if next_parser is None:
                return unit(result)
            else:
                return next_parser

        return Call(old_parser, s, mapped_get_next_parser)
    return mapped_parser
