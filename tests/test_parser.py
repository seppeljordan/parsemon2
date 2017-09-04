import pytest
from parsemon import (bind, chain, character, choice, fail, fmap, literal,
                      many, none_of, run_parser, unit, until)
from parsemon.error import NotEnoughInput, ParsingFailed


def test_literal_parses_a_single_string():
    assert run_parser(literal('a'), 'a') == 'a'

def test_unit_parses_the_empty_string():
    assert run_parser(unit('a'), '') == 'a'

def test_unit_parses_only_the_empty_string():
    with pytest.raises(Exception):
        run_parser(unit('a'), 'a')

def test_fmap_can_replace_parsing_result():
    assert run_parser(
        fmap(
            lambda x: 'b',
            literal('a')),
        'a'
    ) == 'b'

def test_fmap_can_map_1000_time():
    parser = literal('a')
    for i in range(0,1000):
        parser = fmap(lambda x: 'b', parser)
    assert run_parser(parser, 'a') == 'b'

def test_bind_can_chain_two_literal_parsers():
    parser = bind(
        lambda x: literal('b'),
        literal('a'),
    )
    assert run_parser(parser, 'ab') == 'b'

def test_bind_can_chain_3_literal_parsers():
    p = literal('a')
    p = bind(
        lambda x: literal('b'),
        p
    )
    p = bind(
        lambda x: literal('c'),
        p
    )
    assert run_parser(p, 'abc') == 'c'

def test_literal_parser_throws_ParsingFailed_when_seeing_non_matching_string():
    with pytest.raises(ParsingFailed):
        run_parser(literal('a'), 'b')


def test_literal_choice_can_parse_both_possibilities():
    p = choice(
        literal('a'),
        literal('b'),
    )
    assert run_parser(p, 'a') == 'a'
    assert run_parser(p, 'b') == 'b'

def test_choice_can_be_chained_1000_times():
    c = choice(
        literal('a'),
        literal('b'),
    )
    p = unit('')
    for i in range(0,1000):
        p = bind(
            lambda x: c,
            p
        )
    assert run_parser(p, 'a' * 999 + 'b') == 'b'

def test_choice_throws_ParsingFailed_when_both_choices_fail():
    p = choice(
        literal('a'),
        literal('b'),
    )
    with pytest.raises(ParsingFailed):
        run_parser(p, 'c')

def test_choice_should_not_retry_if_the_parser_after_choice_fails():
    p = choice(
        literal('a'),
        literal('aa'),
    )
    p = chain(
        p,
        literal('b')
    )
    with pytest.raises(ParsingFailed):
        run_parser(p, 'aab')

def test_many_parses_empty_strings():
    p = many(
        literal('a')
    )
    assert run_parser(p,'') == []

def test_many_parses_one_occurence():
    p = many(
        literal('a')
    )
    assert run_parser(p, 'a') == ['a']

def test_many_parses_5_occurences():
    p = many(
        literal('a')
    )
    assert run_parser(p, 'aaaaa') == ['a'] * 5

def test_we_can_chain_many_with_something_else():
    p = many(
        literal('a')
    )
    p = bind(
        lambda _: literal('b'),
        p
    )
    assert run_parser(p,'aaaab') == 'b'

def test_until_parses_only_delimiter():
    p = until('a')
    assert run_parser(p, 'a') == ''

def test_until_parses_5_characters_and_delimiter():
    p = until(',')
    assert run_parser(p, 'abcde,') == 'abcde'

def test_until_chained_with_literal_parser_leaves_out_delimiter():
    p = until(',')
    p = bind(
        lambda x: fmap(
            lambda y: [x,y],
            literal('end')
        ),
        p
    )
    assert run_parser(p, 'abcde,end') == ['abcde','end']

def test_parse_none_of_parses_character_when_passed_empty_string():
    p = none_of('')
    assert run_parser(p, 'a') == 'a'

def test_none_of_raises_ParsingFailed_when_encountering_forbidden_char():
    p = none_of('a')
    with pytest.raises(ParsingFailed):
        run_parser(p, 'a')

def test_none_of_raises_ParsingFailed_when_nothing_to_consume():
    p = none_of('a')
    with pytest.raises(ParsingFailed):
        run_parser(p,'')

def test_fail_throws_ParsingFailed_error():
    p = fail('error')
    with pytest.raises(ParsingFailed):
        run_parser(p, '')

def test_character_parses_a_single_A_character():
    p = character()
    assert run_parser(p, 'A') == 'A'

def test_character_raises_ParsingFailed_on_empty_string():
    p = character()
    with pytest.raises(ParsingFailed):
        run_parser(p, '')

def test_character_can_parse_5_characters():
    p = character(n=5)
    assert run_parser(p, '12345') == '12345'

def test_character_raises_ParsingFailed_when_too_few_characters_in_stream():
    p = character(n=5)
    with pytest.raises(NotEnoughInput):
        run_parser(p, '1234')

def test_chain_executes_two_parsers_and_returns_result_of_second_one():
    p = chain(
        literal('a'),
        literal('b')
    )
    assert run_parser(p, 'ab') == 'b'
