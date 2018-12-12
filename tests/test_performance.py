import pytest

from parsemon import choices, literal, many, many1, run_parser
from parsemon.deque import Deque, PyrsistentDeque, Stack


@pytest.mark.parametrize(
    'show_error_messages',
    (
        True,
        False,
    )
)
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
        'a' * 60,
        'b' * 60,
        'c' * 60,
        'ab' * 30,
        'abc' * 20,
        'aabbcc' * 10,
    ),
    ids=lambda x: x[:10],
)
@pytest.mark.benchmark(
    group='general-performance'
)
def test_stack_performance_with_many_choices(
        benchmark,
        stack_implementation,
        input_string,
        show_error_messages,
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
        stack_implementation=stack_implementation,
        show_error_messages=show_error_messages,
    )


if __name__ == '__main__':
    pytest.main(__file__)
