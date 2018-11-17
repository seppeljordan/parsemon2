import pytest

from parsemon import choices, literal, many, run_parser
from parsemon.deque import Deque, PyrsistentDeque, Stack


@pytest.mark.parametrize(
    'stack_implementation',
    (
        Stack,
        Deque,
        PyrsistentDeque,
    )
)
@pytest.mark.parametrize(
    'input_string',
    (
        'a' * 6,
        'b' * 6,
        'c' * 6,
        'ab' * 3,
        'abc' * 2,
    )
)
def test_stack_performance_with_many_choices(
        benchmark,
        stack_implementation,
        input_string
):
    parser = many(
        choices(
            literal('a'),
            literal('b'),
            literal('c'),
        )
    )
    benchmark(
        run_parser,
        parser,
        input_string,
        stack_implementation=stack_implementation
    )
