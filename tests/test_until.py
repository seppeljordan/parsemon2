import hypothesis.strategies as st
import pytest
from hypothesis import given

from parsemon import ParsingFailed, literal, run_parser, until
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


main_parser = literal('a')
delimiter = literal('b')


def test_until_failes_if_parser_fails_and_delimiter_parser_fails(runner):
    with pytest.raises(ParsingFailed):
        runner(until(main_parser, delimiter), 'not_matching_string')


def test_until_returns_empty_tuple_when_only_delimiter_is_found(runner):
    assert runner(until(main_parser, delimiter), 'b').value == tuple()


def test_until_consumes_the_delimiter(runner):
    parsing_result = runner(until(main_parser, delimiter), 'b')
    assert not parsing_result.remaining_input


@given(n=st.integers(min_value=0, max_value=100))
def test_until_returns_n_elements_when_n_elements_are_found(runner, n):
    test_string = 'a' * n + 'b'
    parsing_result = runner(until(main_parser, delimiter), test_string)
    assert len(parsing_result.value) == n


@given(n=st.integers(min_value=0, max_value=100))
def test_until_returns_tuple(runner, n):
    test_string = 'a' * n + 'b'
    parsing_result = runner(until(main_parser, delimiter), test_string)
    assert isinstance(parsing_result.value, tuple)


def test_result_list_contains_results_of_supplied_parser(runner):
    test_string = 'ab'
    parsing_result = runner(until(main_parser, delimiter), test_string)
    assert parsing_result.value == ('a',)
