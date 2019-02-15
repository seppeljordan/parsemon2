from functools import reduce

import pytest
from hypothesis import given
from hypothesis import strategies as st

from parsemon import ParsingFailed, chain, end_of_file, run_parser, unit


def test_that_end_of_file_parser_accepts_empty_input():
    assert run_parser(
        chain(end_of_file(), unit(True)),
        "",
    )


@given(data=st.text())
def test_that_end_of_file_parser_does_only_accept_empty_input(data):
    if data:
        with pytest.raises(ParsingFailed):
            run_parser(
                end_of_file(),
                data,
            )
    else:
        assert run_parser(
            chain(end_of_file(), unit(True)),
            data,
        )


@given(n=st.integers(min_value=1, max_value=1000))
def test_that_end_of_file_parser_parsers_multiple_times(n):
    parser = reduce(
        lambda accu, _: chain(accu, end_of_file()),
        range(0, n),
        unit(True),
    )
    assert run_parser(chain(parser, unit(True)), "")
