import pytest

from parsemon import choices, literal, many, run_parser
from parsemon.stream import CharacterStream, IOStream, StringStream


@pytest.fixture(
    params=(
        CharacterStream,
        StringStream,
        IOStream,
    )
)
def runner(request):
    def fixture(*args, **kwargs):
        return run_parser(*args, stream_implementation=request.param, **kwargs)
    return fixture


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
        input_string,
        runner,
):
    parser = many(choices(
        literal('a'),
        literal('b'),
        literal('c'),
        literal('d'),
    ))
    benchmark(
        runner,
        parser,
        input_string,
    )


if __name__ == '__main__':
    pytest.main(__file__)
