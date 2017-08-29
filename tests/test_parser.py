import pytest
from parsemon import (bind_parser, map_parser, parse_choice, parse_many,
                      parse_string, parse_until, run_parser, unit)
from parsemon.error import ParsingFailed


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

def test_string_parser_throws_ParsingFailed_when_seeing_non_matching_string():
    with pytest.raises(ParsingFailed):
        run_parser(parse_string('a'), 'b')


def test_parse_string_alternatives_can_parse_both_possibilities():
    p = parse_choice(
        parse_string('a'),
        parse_string('b'),
    )
    assert run_parser(p, 'a') == 'a'
    assert run_parser(p, 'b') == 'b'

def test_parse_choice_throws_ParsingFailed_when_both_alternatives_fail():
    p = parse_choice(
        parse_string('a'),
        parse_string('b'),
    )
    with pytest.raises(ParsingFailed):
        run_parser(p, 'c')

def test_parse_many_parses_empty_strings():
    p = parse_many(
        parse_string('a')
    )
    assert run_parser(p,'') == []

def test_parse_many_parses_one_occurence():
    p = parse_many(
        parse_string('a')
    )
    assert run_parser(p, 'a') == ['a']

def test_parse_many_parses_5_occurences():
    p = parse_many(
        parse_string('a')
    )
    assert run_parser(p, 'aaaaa') == ['a'] * 5

def test_parse_until_parses_only_delimiter():
    p = parse_until('a')
    assert run_parser(p, 'a') == ''

def test_parse_until_parses_5_characters_and_delimiter():
    p = parse_until(',')
    assert run_parser(p, 'abcde,') == 'abcde'

def test_parse_until_chained_with_string_parser_leaves_out_delimiter():
    p = parse_until(',')
    p = bind_parser(
        lambda x: map_parser(
            lambda y: [x,y],
            parse_string('end')
        ),
        p
    )
    assert run_parser(p, 'abcde,end') == ['abcde','end']
