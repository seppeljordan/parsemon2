import random

import hypothesis.strategies as st
import pytest
from hypothesis import given

from parsemon.stream import CharacterStream


def random_streams(n=10):
    yield CharacterStream.from_string('')
    for _ in range(1,n):
        length = random.randrange(100)
        yield CharacterStream.from_string(''.join(
            map(
                lambda _: chr(random.randrange(20,1000)),
                range(0,length)
            )
        ))


def test_empty_character_stream_yields_no_next():
    stream = CharacterStream.from_string("")
    assert stream.next() == None


def test_1_character_stream_yields_content_as_next():
    content = '1'
    stream = CharacterStream.from_string(content)
    assert stream.next() == content


def test_1_character_stream_read_yields_content_back():
    content = '1'
    stream = CharacterStream.from_string(content)
    read_content, remainder = stream.read()
    assert read_content == content


@pytest.mark.parametrize(
    'stream',
    random_streams(),
)
def test_that_reading_from_a_stream_reduces_its_length(stream):
    _, new_stream = stream.read()
    if stream:
        assert len(stream) == len(new_stream) + 1
    else:
        assert len(stream) == len(new_stream) == 0


def test_that_empty_character_stream_has_length_zero():
    assert len(CharacterStream.from_string('')) == 0


@pytest.mark.parametrize(
    'content',
    [
        '',
        '123'
    ]
)
def test_that_empty_stream_is_considered_false(content):
    if content:
        assert CharacterStream.from_string(content)
    else:
        assert not CharacterStream.from_string(content)


@pytest.mark.parametrize(
    'stream',
    random_streams(),
)
def test_that_read_gives_same_char_as_next(stream):
    char_read, _ = stream.read()
    assert char_read == stream.next()


@given(text=st.text())
def test_that_characters_read_from_stream_are_in_same_order_as_in_original_string(text):
    stream = CharacterStream.from_string(text)
    for character in text:
        read_char, stream = stream.read()
        assert read_char == character


@given(text=st.text())
def test_that_from_string_and_to_string_yields_identity(text):
    assert CharacterStream.from_string(text).to_string() == text
