from hypothesis import given
from hypothesis import strategies as st

from parsemon import result


@st.composite
def success(draw):
    value = draw(st.integers())
    return result.success(value=value)


@st.composite
def failure(draw):
    return result.failure(
        message=draw(st.text()),
        position=draw(st.integers(min_value=0,))
    )


@given(success())
def test_that_map_value_works_on_success_objects_as_expected(success):
    assert success.value * 2 == success.map_value(lambda x: x*2).value


@given(success())
def test_that_a_success_is_never_considered_a_failure(success):
    assert not success.is_failure()


@given(failure())
def test_that_map_value_does_not_change_a_failure_object(failure):
    assert failure == failure.map_value(lambda _: 0)


@given(failure())
def test_that_a_failure_is_always_considered_a_failure(failure):
    assert failure.is_failure()
