import pytest

from parsemon import choices, literal, run_parser, many
from parsemon.deque import Deque
from parsemon.stack import Stack


@pytest.mark.parametrize(
    'stack_implementation',
    (
        Stack,
        Deque,
    )
)
@pytest.mark.parametrize(
    'input_string',
    (
        'a' * 4,
        'b' * 4,
        'ab' * 2,
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
        )
    )
    benchmark(
        run_parser,
        parser,
        input_string,
        stack_implementation=stack_implementation
    )
