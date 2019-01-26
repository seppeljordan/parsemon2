from hypothesis import given
from hypothesis import strategies as st

from parsemon import result
from parsemon.stream import CharacterStream


@st.composite
def character_stream(draw):
    text = draw(st.text())
    return CharacterStream.from_string(text)


@st.composite
def success(draw):
    stream = draw(character_stream())
    value = draw(st.integers())
    return result.success(value=value, stream=stream)


@st.composite
def failure(draw):
    return result.failure(
        message=draw(st.text()),
        stream=draw(character_stream())
    )


@given(success())
def test_that_map_value_works_on_success_objects_as_expected(success):
    assert success.value * 2 == success.map_value(lambda x: x*2).value


@given(success())
def test_that_a_success_is_never_considered_a_failure(success):
    assert not success.is_failure()


@given(success(), character_stream())
def test_that_map_stream_does_not_change_the_value_of_success_objects(
        success,
        character_stream,
):
    assert (
        success.value ==
        success.map_stream(lambda _: character_stream).value
    )


@given(success())
def test_that_map_value_never_changes_the_stream_of_success_objects(
        success,
):
    assert (
        success.stream ==
        success.map_value(lambda _: 0).stream
    )


@given(failure())
def test_that_map_value_does_not_change_a_failure_object(failure):
    assert failure == failure.map_value(lambda _: 0)


@given(failure(), character_stream())
def test_that_map_stream_does_not_change_the_message_of_failure(
        failure,
        character_stream,
):
    assert (
        failure.message ==
        failure.map_stream(lambda _: character_stream).message
    )


@given(failure())
def test_that_a_failure_is_always_considered_a_failure(failure):
    assert failure.is_failure()
