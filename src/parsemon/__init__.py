from parsemon.trampoline import Call, Result, with_trampoline


def run_parser(p, input_string):
    parsing_result, rest = with_trampoline(p)(input_string, lambda x: None)
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
                return Call(next_parser, rest)
        else:
            raise Exception("parse error")
    return parser


def unit(u):
    def parser(s, get_next_parser):
        next_parser = get_next_parser(u)
        if next_parser is None:
            return Result((u, s))
        else:
            return Call(next_parser, s)

    return parser


def map_parser(mapping, parser):
    def parser(s, get_next_parser):
        def mapped_get_next_parser(unmapped_result):
            result = mapping(unmapped_result)
            next_parser = get_next_parser(result)
            if next_parser is None:
                return unit(result)
            else:
                return next_parser
        return Call(parser, mapped_get_next_parser)
    return parser
