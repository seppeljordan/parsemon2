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


@given(random_stream=strategies.stream())
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


@given(stream=strategies.stream())
def test_that_next_on_stream_that_was_emptied_gives_none(
    stream,
):
    while stream.next() is not None:
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


@given(content=st.text(min_size=1))
def test_peeking_next_character_does_not_change_result_of_to_string(
    content: str, stream_implementation
) -> None:
    stream = stream_implementation.from_string(content)
    stream.next()
    assert stream.to_string() == content
