from functools import reduce

import pytest

from parsemon.deque import Deque, Stack, deque_empty


@pytest.fixture(
    params=(
        Stack,
        Deque,
    )
)
def container(request):
    return request.param


@pytest.fixture(
    params=[
        (
            tuple(),
            tuple(),
        ),
        (
            (1,),
            tuple(),
        ),
        (
            tuple(),
            (2,),
        ),
        (
            (1,),
            (2,),
        ),
    ]
)
def deque(request, container):
    front, back = request.param
    return reduce(
        lambda accu, item: accu.push(item),
        reversed(front),
        reduce(
            lambda accu, item: accu.append(item),
            back,
            container()
        )
    )


def test_new_stack_is_empty(container):
    assert container().empty()


def test_when_we_add_elem_to_stack_it_is_not_empty(container):
    assert not container().push('a').empty()


def test_when_we_push_an_elem_and_then_top_we_get_the_same_elem(container):
    value = 'a'
    assert container().push('a').top() == value


def test_when_we_push_and_pop_we_get_the_empty_stack(container):
    assert container().push('a').pop().empty()


def test_pop_on_empty_deque_return_deque_empty(container):
    assert container().top() is deque_empty


def test_iterating_over_stack_sees_pushed_elems_in_reverse(container):
    elems = [1, 2, 3]
    s = container()
    for e in elems:
        s = s.push(e)
    elems.reverse()
    assert list(s) == elems


def test_if_we_append_an_item_it_is_the_last_item_popped(container):
    elems = [1, 2, 3]
    s = container()
    for e in elems:
        s = s.push(e)
    s = s.append(0)
    elems.reverse()
    assert list(s) == elems + [0]


def test_reversed_iterates_over_elements_in_order_of_push(container):
    elems = [1, 2, 3]
    s = container()
    for e in elems:
        s = s.push(e)
    assert elems == list(reversed(s))


def test_that_flipped_stack_has_reversed_ordering(container):
    elems = [1, 2, 3]
    s = container()
    for e in elems:
        s = s.push(e)
    assert elems == list(s.flipped())


def test_that_pop_from_empty_deque_returns_deque_empty(deque):
    if deque.empty():
        assert deque.pop() is deque_empty
    else:
        assert deque.pop() is not deque_empty


def test_that_len_of_empty_deque_is_zero(deque):
    if deque.empty():
        assert not len(deque)
    else:
        assert len(deque)


def test_that_push_increases_len_by_1(deque):
    assert len(deque) + 1 == len(deque.push(1))


def test_that_push_and_top_yields_the_item_pushed(deque):
    class TestClass:
        pass

    assert deque.push(TestClass).top() is TestClass


def test_that_pop_reduces_length_by_one(deque):
    if deque.empty():
        assert True
    else:
        assert len(deque.pop()) + 1 == len(deque)


def test_that_push_and_pop_lead_to_deque_having_same_top_again(deque):
    if deque.empty():
        assert True
    else:
        assert deque.top() is deque.push(1).pop().top()


def test_that_append_increases_length_by_1(deque):
    assert len(deque) + 1 == len(deque.append(1))


def test_that_last_element_is_that_one_most_recently_appended(deque):
    class TestValue:
        pass
    assert deque.append(TestValue).last() is TestValue


@pytest.mark.parametrize(
    "items",
    (
        [1, 2, 3, 4],
        [],
        [None],
    )
)
def test_that_appending_elements_and_poping_them_yields_same_order(
        deque,
        items
):
    populated_deque = reduce(
        lambda d, item: d.append(item),
        items,
        deque
    )

    deque_without_prefilled_items = reduce(
        lambda d, _: d.pop(),
        range(0, len(deque)),
        populated_deque
    )

    for item in items:
        next_item = deque_without_prefilled_items.top()
        assert next_item is item
        deque_without_prefilled_items = deque_without_prefilled_items.pop()


def test_top_and_last_on_empty_stack_return_deque_empty(deque):
    if deque.empty():
        assert deque.top() is deque_empty
        assert deque.last() is deque_empty
    else:
        deque.top()
