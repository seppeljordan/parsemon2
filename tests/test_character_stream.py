import random

import hypothesis.strategies as st
import pytest
from hypothesis import given

from parsemon.stream import IOStream, StringStream

from . import strategies


@pytest.fixture(
    params=(
        StringStream,
        IOStream,
    ),
    scope="session",
)
def stream_implementation(request):
    yield request.param


def test_empty_character_stream_yields_no_next(stream_implementation):
    stream = stream_implementation.from_string("")
    assert stream.next() is None


def test_1_character_stream_yields_content_as_next(stream_implementation):
    content = "1"
    stream = stream_implementation.from_string(content)
    assert stream.next() == content


def test_1_character_stream_read_yields_content_back(stream_implementation):
    content = "1"
    stream = stream_implementation.from_string(content)
    read_content = stream.read()
    assert read_content == content


def random_strings():
    yield ""
    for _ in range(1, 10):
        length = random.randrange(100)
        yield "".join(map(lambda _: chr(random.randrange(20, 1000)), range(0, length)))


@pytest.fixture(params=random_strings())
def random_stream(request, stream_implementation):
    return stream_implementation.from_string(request.param)


@given(stream=strategies.stream(min_size=1))
def test_that_reading_from_a_stream_reduces_its_length(stream):
    original_length = len(stream)
    stream.read()
    assert original_length == len(stream) + 1


def test_that_empty_character_stream_has_length_zero(stream_implementation):
    assert len(stream_implementation.from_string("")) == 0


@pytest.mark.parametrize("content", ["", "123"])
def test_that_empty_stream_is_considered_false(content, stream_implementation):
    if content:
        assert stream_implementation.from_string(content)
    else:
        assert not stream_implementation.from_string(content)


def test_that_read_gives_same_char_as_next(random_stream):
    expected_char = random_stream.next()
    assert random_stream.read() == expected_char


@given(text=st.text())
def test_that_characters_read_from_stream_are_in_same_order_as_original_string(
    text,
    stream_implementation,
):
    stream = stream_implementation.from_string(text)
    for character in text:
        assert stream.read() == character


@given(text=st.text())
def test_that_from_string_and_to_string_yields_identity(text, stream_implementation):
    assert stream_implementation.from_string(text).to_string() == text


@given(text=st.text())
def test_that_next_on_stream_that_was_emptied_gives_none(
    text,
    stream_implementation,
):
    stream = stream_implementation.from_string(text)
    for _ in range(0, len(stream)):
        stream.read()
    assert stream.next() is None


@given(text=st.text(min_size=1))
def test_that_reading_stream_advances_its_position_by_one(
    text,
    stream_implementation,
):
    stream = stream_implementation.from_string(text)
    original_position = stream.position()
    stream.read()

    assert original_position == stream.position() - 1


@given(stream=strategies.stream(min_size=1))
def test_that_stream_can_be_reset(stream):
    reset_point = stream.get_reset_point()
    character_read = stream.read()
    stream.reset_stream(reset_point)
    assert stream.read() == character_read
