import random

import hypothesis.strategies as st
import pytest
from hypothesis import given

from parsemon.stream import CharacterStream, IOStream, StringStream


@pytest.fixture(
    params=(
        CharacterStream,
        StringStream,
        IOStream,
    )
)
def stream_implementation(request):
    yield request.param


def test_empty_character_stream_yields_no_next(stream_implementation):
    stream = stream_implementation.from_string("")
    assert stream.next() is None


def test_1_character_stream_yields_content_as_next(stream_implementation):
    content = '1'
    stream = stream_implementation.from_string(content)
    assert stream.next() == content


def test_1_character_stream_read_yields_content_back(stream_implementation):
    content = '1'
    stream = stream_implementation.from_string(content)
    read_content, remainder = stream.read()
    assert read_content == content


def random_strings():
    yield ''
    for _ in range(1, 10):
        length = random.randrange(100)
        yield ''.join(
            map(
                lambda _: chr(random.randrange(20, 1000)),
                range(0, length)
            )
        )


@pytest.fixture(
    params=random_strings()
)
def random_stream(request, stream_implementation):
    return stream_implementation.from_string(request.param)


def test_that_reading_from_a_stream_reduces_its_length(random_stream):
    _, new_stream = random_stream.read()
    if random_stream:
        assert len(random_stream) == len(new_stream) + 1
    else:
        assert len(random_stream) == len(new_stream) == 0


def test_that_empty_character_stream_has_length_zero(stream_implementation):
    assert len(stream_implementation.from_string('')) == 0


@pytest.mark.parametrize(
    'content',
    [
        '',
        '123'
    ]
)
def test_that_empty_stream_is_considered_false(content, stream_implementation):
    if content:
        assert stream_implementation.from_string(content)
    else:
        assert not stream_implementation.from_string(content)


def test_that_read_gives_same_char_as_next(random_stream):
    char_read, _ = random_stream.read()
    assert char_read == random_stream.next()


@given(text=st.text())
def test_that_characters_read_from_stream_are_in_same_order_as_original_string(
        text,
        stream_implementation,
):
    stream = stream_implementation.from_string(text)
    for character in text:
        read_char, stream = stream.read()
        assert read_char == character


@given(text=st.text())
def test_that_from_string_and_to_string_yields_identity(
        text,
        stream_implementation
):
    assert stream_implementation.from_string(text).to_string() == text


@given(text=st.text())
def test_that_next_on_stream_that_was_emptied_gives_none(
        text,
        stream_implementation,
):
    stream = stream_implementation.from_string(text)
    for _ in range(0, len(stream)):
        stream = stream.read()[1]
    assert stream.next() is None


@given(text=st.text())
def test_that_reading_stream_advances_its_position_by_one_unless_it_is_empty(
        text,
        stream_implementation,
):
    stream = stream_implementation.from_string(text)
    if stream:
        assert stream.position() == stream.read()[1].position() - 1
    else:
        assert stream.position() == stream.read()[1].position()
