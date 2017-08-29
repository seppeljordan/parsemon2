import pytest
from parsemon import map_parser, parse_string, run_parser, unit


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
