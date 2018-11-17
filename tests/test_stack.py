import pytest

from parsemon.stack import Stack, StackEmptyError
from parsemon.deque import Deque


@pytest.fixture(
    params=(
        Stack,
        Deque,
    )
)
def container(request):
    return request.param


def test_new_stack_is_empty(container):
    assert container().empty()


def test_when_we_add_elem_to_stack_it_is_not_empty(container):
    assert not container().push('a').empty()


def test_when_we_push_an_elem_and_then_top_we_get_the_same_elem(container):
    value = 'a'
    assert container().push('a').top() == value


def test_top_on_empty_stack_raises_an_StackEmptyError(container):
    with pytest.raises(StackEmptyError):
        container().top()

def test_when_we_push_and_pop_we_get_the_empty_stack(container):
    assert container().push('a').pop().empty()

def test_pop_on_empty_stack_raises_StackEmptyError(container):
    with pytest.raises(StackEmptyError):
        container().pop()


def test_iterating_over_stack_sees_pushed_elems_in_reverse(container):
    elems = [1,2,3]
    s = container()
    for e in elems:
        s = s.push(e)
    elems.reverse()
    assert list(s) == elems


def test_if_we_append_an_item_it_is_the_last_item_popped(container):
    elems = [1,2,3]
    s = container()
    for e in elems:
        s = s.push(e)
    s = s.append(0)
    elems.reverse()
    assert list(s) == elems + [0]


def test_reversed_iterates_over_elements_in_order_of_push(container):
    elems = [1,2,3]
    s = container()
    for e in elems:
        s = s.push(e)
    assert elems == list(reversed(s))


def test_that_flipped_stack_has_reversed_ordering(container):
    elems = [1,2,3]
    s = container()
    for e in elems:
        s = s.push(e)
    assert elems == list(s.flipped())


def test_that_len_of_empty_stack_is_0(container):
    assert len(container()) == 0


def test_that_len_of_stack_with_one_elem_is_1(container):
    assert len(container().push(1)) == 1
