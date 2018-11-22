import pytest

from parsemon import choices, literal, many, run_parser, many1
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
        'a' * 600,
        'b' * 600,
        'c' * 600,
        'ab' * 300,
        'abc' * 200,
        'aabbcc' * 100,
    ),
    ids=lambda x: x[:10],
)
def test_stack_performance_with_many_choices(
        benchmark,
        stack_implementation,
        input_string,
):
    parser = many(choices(
        literal('a'),
        literal('b'),
        literal('c'),
        literal('d'),
    ))
    benchmark(
        run_parser,
        parser,
        input_string,
        stack_implementation=stack_implementation
    )
