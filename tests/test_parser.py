import pytest
from parsemon import bind_parser, map_parser, parse_string, run_parser, unit


def test_string_parses_a_single_string():
    assert run_parser(parse_string('a'), 'a') == 'a'

def test_unit_parses_the_empty_string():
    assert run_parser(unit('a'), '') == 'a'

def tests_unit_parses_only_the_empty_string():
    with pytest.raises(Exception):
        run_parser(unit('a'), 'a')

def test_map_parser_can_replace_parsing_result():
    assert run_parser(
        map_parser(
            lambda x: 'b',
            parse_string('a')),
        'a'
    ) == 'b'

def test_map_parser_can_map_1000_time():
    parser = parse_string('a')
    for i in range(0,1000):
        parser = map_parser(lambda x: 'b', parser)
    assert run_parser(parser, 'a') == 'b'

def test_bind_can_chain_two_string_parsers():
    parser = bind_parser(
        lambda x: parse_string('b'),
        parse_string('a'),
    )
    assert run_parser(parser, 'ab') == 'b'

def test_bind_can_chain_3_string_parsers():
    p = parse_string('a')
    p = bind_parser(
        lambda x: parse_string('b'),
        p
    )
    p = bind_parser(
        lambda x: parse_string('c'),
        p
    )
    assert run_parser(p, 'abc') == 'c'
