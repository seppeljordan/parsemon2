import pytest

from parsemon import (bind, chain, character, choice, choices, enclosed_by,
                      fail, fmap, literal, many, many1, none_of, one_of,
                      run_parser, seperated_by, unit, until, whitespace)
from parsemon.error import NotEnoughInput, ParsingFailed
from parsemon.sourcemap import display_location


@pytest.fixture(
    params=(
        'with_error_messages',
        'without_error_messages',
    )
)
def runner(request):
    if request.param == 'with_error_messages':
        def fixture(*args, **kwargs):
            return run_parser(*args, show_error_messages=True, **kwargs)
    else:
        def fixture(*args, **kwargs):
            return run_parser(*args, show_error_messages=False, **kwargs)
    return fixture



def test_literal_parses_a_single_string(runner):
    assert runner(literal('a'), 'a') == 'a'

def test_unit_parses_the_empty_string(runner):
    assert runner(unit('a'), '') == 'a'

def test_unit_parses_only_the_empty_string(runner):
    with pytest.raises(Exception):
        runner(unit('a'), 'a')

def test_fmap_can_replace_parsing_result(runner):
    assert runner(
        fmap(
            lambda x: 'b',
            literal('a')),
        'a'
    ) == 'b'

def test_fmap_can_map_1000_time(runner):
    parser = literal('a')
    for i in range(0,1000):
        parser = fmap(lambda x: 'b', parser)
    assert runner(parser, 'a') == 'b'

def test_bind_can_chain_two_literal_parsers(runner):
    parser = bind(
        literal('a'),
        lambda x: literal('b'),
    )
    assert runner(parser, 'ab') == 'b'

def test_bind_can_chain_3_literal_parsers(runner):
    p = literal('a')
    p = bind(
        p,
        lambda x: literal('b'),
    )
    p = bind(
        p,
        lambda x: literal('c'),
    )
    assert runner(p, 'abc') == 'c'

def test_literal_parser_throws_ParsingFailed_when_seeing_non_matching_string(runner):
    with pytest.raises(ParsingFailed):
        runner(literal('a'), 'b')


def test_literal_choice_can_parse_both_possibilities(runner):
    p = choice(
        literal('a'),
        literal('b'),
    )
    assert runner(p, 'a') == 'a'
    assert runner(p, 'b') == 'b'

def test_choice_can_be_chained_1000_times(runner):
    c = choice(
        literal('a'),
        literal('b'),
    )
    p = unit('')
    for i in range(0,1000):
        p = bind(
            p,
            lambda x: c,
        )
    assert runner(p, 'a' * 999 + 'b') == 'b'

def test_choice_throws_ParsingFailed_when_both_choices_fail(runner):
    p = choice(
        literal('a'),
        literal('b'),
    )
    with pytest.raises(ParsingFailed):
        runner(p, 'c')

def test_choice_should_not_retry_if_the_parser_after_choice_fails(runner):
    p = choice(
        literal('a'),
        literal('aa'),
    )
    p = chain(
        p,
        literal('b')
    )
    with pytest.raises(ParsingFailed):
        runner(p, 'aab')

def test_many_parses_empty_strings(runner):
    p = many(
        literal('a')
    )
    assert runner(p,'') == []

def test_many_parses_one_occurence(runner):
    p = many(
        literal('a')
    )
    assert runner(p, 'a') == ['a']

def test_many_parses_5_occurences(runner):
    p = many(
        literal('a')
    )
    assert runner(p, 'aaaaa') == ['a'] * 5

def test_we_can_chain_many_with_something_else(runner):
    p = many(
        literal('a')
    )
    p = bind(
        p,
        lambda _: literal('b'),
    )
    assert runner(p,'aaaab') == 'b'

def test_until_parses_only_delimiter(runner):
    p = until('a')
    assert runner(p, 'a') == ''

def test_until_parses_5_characters_and_delimiter(runner):
    p = until(',')
    assert runner(p, 'abcde,') == 'abcde'

def test_until_chained_with_literal_parser_leaves_out_delimiter(runner):
    p = until(',')
    p = bind(
        p,
        lambda x: fmap(
            lambda y: [x,y],
            literal('end')
        ),
    )
    assert runner(p, 'abcde,end') == ['abcde','end']

def test_parse_none_of_parses_character_when_passed_empty_string(runner):
    p = none_of('')
    assert runner(p, 'a') == 'a'

def test_none_of_raises_ParsingFailed_when_encountering_forbidden_char(runner):
    p = none_of('a')
    with pytest.raises(ParsingFailed):
        runner(p, 'a')

def test_none_of_raises_ParsingFailed_when_nothing_to_consume(runner):
    p = none_of('a')
    with pytest.raises(ParsingFailed):
        runner(p,'')

def test_fail_throws_ParsingFailed_error(runner):
    p = fail('error')
    with pytest.raises(ParsingFailed):
        runner(p, '')

def test_character_parses_a_single_A_character(runner):
    p = character()
    assert runner(p, 'A') == 'A'

def test_character_raises_ParsingFailed_on_empty_string(runner):
    p = character()
    with pytest.raises(ParsingFailed):
        runner(p, '')

def test_character_can_parse_5_characters(runner):
    p = character(n=5)
    assert runner(p, '12345') == '12345'

def test_character_raises_ParsingFailed_when_too_few_characters_in_stream(runner):
    p = character(n=5)
    with pytest.raises(NotEnoughInput):
        runner(p, '1234')

def test_chain_executes_two_parsers_and_returns_result_of_second_one(runner):
    p = chain(
        literal('a'),
        literal('b')
    )
    assert runner(p, 'ab') == 'b'


def test_chain_can_take_3_parsers_as_args(runner):
    p = chain(
        literal('a'),
        literal('b'),
        literal('c')
    )
    assert runner(p, 'abc') == 'c'


def test_if_a_choice_failes_in_the_middle_of_chain_it_retries_other_option(runner):
    p = choice(
        chain(
            literal('a'),
            literal('a')
        ),
        chain(
            literal('a'),
            literal('b'),
        )
    )
    assert runner(p, 'ab') == 'b'

def test_many1_fails_for_empty_strings(runner):
    p = many1(literal('a'))
    with pytest.raises(ParsingFailed):
        runner(p, '')

def test_many1_behaves_like_many_for_1_occurence(runner):
    p = literal('a')
    assert runner(many1(p), 'a') == runner(many(p), 'a')

def test_failure_of_literal_contains_expected_string():
    p = literal('abcde')
    with pytest.raises(ParsingFailed) as err:
        run_parser(p, 'xxxxx')
    assert 'abcde' in str(err.value)

def test_failure_of_choice_of_2_literals_should_contain_both_literals():
    p = choice(
        literal('first_literal'),
        literal('second_literal'),
    )
    with pytest.raises(ParsingFailed) as err:
        run_parser(p, 'xxxxxxxxxxxxxxxxxxx')
    assert 'first_literal' in str(err.value)
    assert 'second_literal' in str(err.value)

def test_failure_of_choice_of_3_literals_should_contain_all_3_literal():
    p = choice(
        literal('first'),
        choice(
            literal('second'),
            literal('third')
        )
    )
    with pytest.raises(ParsingFailed) as err:
        run_parser(p, 'xxxxxxxxxxxxxxxx')
    error_message = str(err.value)
    assert 'first' in error_message
    assert 'second' in error_message
    assert 'third' in error_message

def test_that_error_message_respects_ordering_of_failing_choices():
    p = choice(
        literal('first'),
        literal('second'),
    )
    with pytest.raises(ParsingFailed) as err:
        run_parser(p, 'xxxxxxxxxxxxxx')
    error_message = str(err.value)
    assert 'second' not in error_message.split('first')[1]
    assert 'first' in error_message.split('second')[1]


def test_that_error_message_order_is_preserved_with_3_choices():
    p = choice(
        literal('first'),
        choice(
            literal('second'),
            literal('third'),
        )
    )
    with pytest.raises(ParsingFailed) as err:
        run_parser(p, 'xxxxxxxxxxxxxx')
    error_message = str(err.value)
    print(error_message)
    assert 'second' in error_message.split('first')[0]
    assert 'third' in error_message.split('first')[0]
    assert 'first' in error_message.split('second')[1]
    assert 'third' in error_message.split('second')[0]


def test_a_simple_failing_parser_prints_column_0_as_error():
    p = fail('error')
    with pytest.raises(ParsingFailed) as err:
        run_parser(p, '')
    assert display_location(line=1, column=0) in str(err.value)

def test_a_simple_failing_parser_after_2_newlines_outputs_linenumber_3_in_error():
    p = chain(
        literal('\n\n'),
        fail('error')
    )
    with pytest.raises(ParsingFailed) as err:
        run_parser(p,'\n\nx')
    assert display_location(line=3, column=0) in str(err.value)

def test_one_of_fails_if_trying_to_parse_something_not_in_set(runner):
    with pytest.raises(ParsingFailed):
        runner(one_of('123'), '4')

def test_onf_of_succeeds_if_trying_to_parse_something_in_the_set(runner):
    assert runner(one_of('123'), '1') == '1'

def test_seperated_by_empty(runner):
    assert runner(
        seperated_by(
            literal('a'),
            literal(',')
        ),
        ''
    ) == []

def test_seperated_by_one_element(runner):
    assert runner(
        seperated_by(
            literal('a'),
            literal(',')
        ),
        'a'
    ) == ['a']

def test_seperated_by_five_elemts(runner):
    assert runner(
        seperated_by(
            literal('a'),
            literal(',')
        ),
        'a,a,a,a,a'
    ) == ['a','a','a','a','a']

def test_seperated_by_1000_elements(runner):
    assert runner(
        seperated_by(
            literal('a'),
            literal(',')
        ),
        'a' + ',a' * 999
    ) == ['a'] * 1000

def test_enclosed_by(runner):
    assert runner(
        enclosed_by(
            literal('a'),
            literal('"')
        ),
        '"a"'
    ) == 'a'

def test_choices(runner):
    assert runner(
        choices(
            literal('a'),
            literal('b'),
            literal('c')
        ),
        'b'
    ) == 'b'


def test_whitespace_parses_regular_space_character(runner):
    assert runner(whitespace, "\u0020") == "\u0020"


def test_whitespace_parses_tab_char(runner):
    assert runner(whitespace, '\t') == '\t'


def test_whitespace_parses_newline_char(runner):
    assert runner(whitespace, '\n') == '\n'


def test_that_or_operator_works_as_expected(runner):
    assert runner(whitespace | literal('a'), ' ') == ' '
    assert runner(whitespace | literal('a'), 'a') == 'a'
