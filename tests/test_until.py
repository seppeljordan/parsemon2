import pytest

from parsemon import bind, chain, fmap, literal, run_parser, unit, until
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


def test_until_parses_empty_string_when_finding_delimiter_immediately(runner):
    p = bind(
        until('a'),
        lambda s: chain(
            literal('a'),
            unit('')
        )
    )
    assert runner(p, 'a').value == ''


def test_until_parses_5_characters_but_not_the_delimiter(runner):
    p = bind(
        until(','),
        lambda s: chain(
            literal(','),
            unit(s)
        )
    )
    assert runner(p, 'abcde,').value == 'abcde'


def test_until_chained_with_literal_requires_explicit_delimiter_parsing(
        runner
):
    """Test that `until` parser chained with `literal` parser requires
    explicit parsing of the specified delimiter
    """
    p = until(',')
    p = bind(
        p,
        lambda x: fmap(
            lambda y: [x, y],
            chain(
                literal(','),
                literal('end')
            )
        ),
    )
    assert runner(p, 'abcde,end').value == ['abcde', 'end']
