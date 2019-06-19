import hypothesis.strategies as st
import pytest
from hypothesis import example, given

from parsemon import (bind, chain, character, choice, choices, enclosed_by,
                      fail, fmap, literal, many, many1, none_of, one_of,
                      run_parser, seperated_by, try_parser, unit, whitespace)
from parsemon.error import ParsingFailed
from parsemon.sourcemap import display_location
from parsemon.stream import CharacterStream, StringStream


@pytest.fixture(
    params=(
        CharacterStream,
        StringStream,
    )
)
def runner(request):
    def fixture(*args, **kwargs):
        return run_parser(*args, stream_implementation=request.param, **kwargs)
    return fixture


@given(text=st.text())
@example(text='')
def test_literal_parses_a_single_string(runner, text):
    assert runner(literal(text), text).value == text


@given(char=st.characters(), text=st.text())
def test_that_unit_returns_char_given_to_unit(runner, char, text):
    assert runner(unit(char), text).value == char


def test_fmap_can_replace_parsing_result(runner):
    parser = fmap(
        lambda x: 'b',
        literal('a')
    )
    assert runner(parser, 'a').value == 'b'


def test_fmap_can_map_1000_times(runner):
    parser = literal('a')
    for i in range(0, 1000):
        parser = fmap(lambda x: 'b', parser)
    assert runner(parser, 'a').value == 'b'


@given(
    a=st.characters(),
    b=st.characters(),
)
def test_bind_can_chain_two_literal_parsers(runner, a, b):
    parser = bind(
        literal(a),
        lambda x: literal(b),
    )
    assert runner(parser, a + b).value == b


@given(
    a=st.text(),
    b=st.text(),
    c=st.text(),
)
def test_bind_can_chain_3_literal_parsers(runner, a, b, c):
    p = literal(a)
    p = bind(
        p,
        lambda x: literal(b),
    )
    p = bind(
        p,
        lambda x: literal(c),
    )
    assert runner(p, a + b + c).value == c


def test_literal_parser_throws_ParsingFailed_when_seeing_non_matching_string(
        runner
):
    with pytest.raises(ParsingFailed):
        runner(literal('a'), 'b')


@given(
    a=st.text(min_size=1),
    b=st.text(min_size=1),
)
def test_literal_choice_can_parse_both_possibilities(runner, a, b):
    # we must order the two strings because of the possibility that a
    # can be a prefix of b or the other way around
    p = choice(
        try_parser(literal(a)),
        literal(b),
    ) if len(a) > len(b) else choice(
        try_parser(literal(b)),
        literal(a),
    )
    assert runner(p, a).value == a
    assert runner(p, b).value == b


def test_choice_can_be_chained_1000_times(runner):
    c = choice(
        literal('a'),
        literal('b'),
    )
    p = unit('')
    for i in range(0, 1000):
        p = bind(
            p,
            lambda x: c,
        )
    assert runner(p, 'a' * 999 + 'b').value == 'b'


def test_choice_throws_ParsingFailed_when_both_choices_fail(runner):
    p = choice(
        literal('a'),
        literal('b'),
    )
    with pytest.raises(ParsingFailed):
        runner(p, 'c')


def test_choice_should_not_retry_if_the_parser_after_choice_fails(runner):
    p = choice(
        literal('a'),  # this should match the incomming input
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
    assert runner(p, '').value == []


def test_many_parses_one_occurence(runner):
    p = many(
        literal('a')
    )
    assert runner(p, 'a').value == ['a']


def test_many_parses_5_occurences(runner):
    p = many(
        literal('a')
    )
    assert runner(p, 'aaaaa').value == ['a'] * 5


def test_we_can_chain_many_with_something_else(runner):
    p = many(
        literal('a')
    )
    p = bind(
        p,
        lambda _: literal('b'),
    )
    assert runner(p, 'aaaab').value == 'b'


@given(text=st.text(min_size=1, max_size=1))
def test_parse_none_of_parses_character_when_passed_empty_string(runner, text):
    p = none_of('')
    assert runner(p, text).value == text


def test_none_of_raises_ParsingFailed_when_encountering_forbidden_char(runner):
    p = none_of('a')
    with pytest.raises(ParsingFailed):
        runner(p, 'a')


def test_none_of_raises_ParsingFailed_when_nothing_to_consume(runner):
    p = none_of('a')
    with pytest.raises(ParsingFailed):
        runner(p, '')


def test_fail_throws_ParsingFailed_error(runner):
    p = fail('error')
    with pytest.raises(ParsingFailed):
        runner(p, '')


@given(text=st.text(min_size=1, max_size=1))
def test_character_parses_a_single_character(runner, text):
    p = character()
    assert runner(p, text).value == text


def test_character_raises_ParsingFailed_on_empty_string(runner):
    p = character()
    with pytest.raises(ParsingFailed):
        runner(p, '')


def test_character_can_parse_5_characters(runner):
    p = character(n=5)
    assert runner(p, '12345').value == '12345'


def test_character_raises_ParsingFailed_when_too_few_characters_in_stream(
        runner
):
    p = character(n=5)
    with pytest.raises(ParsingFailed):
        runner(p, '1234')


def test_chain_executes_two_parsers_and_returns_result_of_second_one(runner):
    p = chain(
        literal('a'),
        literal('b')
    )
    assert runner(p, 'ab').value == 'b'


def test_chain_can_take_3_parsers_as_args(runner):
    p = chain(
        literal('a'),
        literal('b'),
        literal('c')
    )
    assert runner(p, 'abc').value == 'c'


def test_if_a_choice_failes_in_the_middle_of_chain_it_retries_other_option(
        runner
):
    p = choice(
        try_parser(chain(
            literal('a'),
            literal('a')
        )),
        chain(
            literal('a'),
            literal('b'),
        )
    )
    assert runner(p, 'ab').value == 'b'


def test_many1_fails_for_empty_strings(runner):
    p = many1(literal('a'))
    with pytest.raises(ParsingFailed):
        runner(p, '')


def test_many1_behaves_like_many_for_1_occurence(runner):
    p = literal('a')
    assert runner(many1(p), 'a').value == runner(many(p), 'a').value


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
    assert 'second' in error_message.split('first')[1]
    assert 'first' in error_message.split('second')[0]


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
    assert 'second' in error_message.split('first')[1]
    assert 'third' in error_message.split('first')[1]
    assert 'first' in error_message.split('second')[0]
    assert 'third' in error_message.split('second')[1]


def test_a_simple_failing_parser_prints_column_0_as_error():
    p = fail('error')
    with pytest.raises(ParsingFailed) as err:
        run_parser(p, '')
    assert display_location(line=1, column=0) in str(err.value)


# Large values for n create test run times to large
@given(n=st.integers(min_value=0, max_value=100))
def test_simple_failing_parser_after_n_newlines_has_linenumber_n1_in_error(
        n,
        runner,
):
    p = chain(
        literal('\n' * n),
        fail('error')
    )
    with pytest.raises(ParsingFailed) as err:
        runner(p, ('\n' * n) + 'x')
    assert display_location(line=n + 1, column=0) in str(err.value)


def test_one_of_fails_if_trying_to_parse_something_not_in_set(runner):
    with pytest.raises(ParsingFailed):
        runner(one_of('123'), '4')


def test_onf_of_succeeds_if_trying_to_parse_something_in_the_set(runner):
    assert runner(one_of('123'), '1').value == '1'


def test_seperated_by_empty(runner):
    assert runner(
        seperated_by(
            literal('a'),
            literal(',')
        ),
        ''
    ).value == []


def test_seperated_by_one_element(runner):
    assert runner(
        seperated_by(
            literal('a'),
            literal(',')
        ),
        'a'
    ).value == ['a']


def test_seperated_by_five_elemts(runner):
    assert runner(
        seperated_by(
            literal('a'),
            literal(',')
        ),
        'a,a,a,a,a'
    ).value == ['a', 'a', 'a', 'a', 'a']


def test_seperated_by_1000_elements(runner):
    assert runner(
        seperated_by(
            literal('a'),
            literal(',')
        ),
        'a' + ',a' * 999
    ).value == ['a'] * 1000


def test_enclosed_by(runner):
    assert runner(
        enclosed_by(
            literal('a'),
            literal('"')
        ),
        '"a"'
    ).value == 'a'


def test_choices(runner):
    assert runner(
        choices(
            literal('a'),
            literal('b'),
            literal('c')
        ),
        'b'
    ).value == 'b'


def test_whitespace_parses_regular_space_character(runner):
    assert runner(whitespace, "\u0020").value == "\u0020"


def test_whitespace_parses_tab_char(runner):
    assert runner(whitespace, '\t').value == '\t'


def test_whitespace_parses_newline_char(runner):
    assert runner(whitespace, '\n').value == '\n'


def test_that_or_operator_works_as_expected(runner):
    assert runner(whitespace | literal('a'), ' ').value == ' '
    assert runner(whitespace | literal('a'), 'a').value == 'a'


def test_that_fmap_does_not_change_error_messages(runner):
    parser = literal('a')
    with pytest.raises(ParsingFailed) as error_message_without_fmap:
        runner(parser, 'b')
    with pytest.raises(ParsingFailed) as error_message_with_fmap:
        runner(fmap(lambda char: char + 1, parser), 'b')
    assert (
        str(error_message_without_fmap.value) ==
        str(error_message_with_fmap.value)
    )


@given(text=st.text())
def test_that_unit_parser_returns_complete_input_string_as_not_consumed(
        text,
        runner,
):
    parser = unit(True)
    assert runner(parser, text).remaining_input == text
