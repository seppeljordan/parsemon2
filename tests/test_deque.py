from functools import reduce

import pytest

from parsemon.deque import Deque
from parsemon.stack import StackEmptyError


@pytest.fixture(
    params=[
        Deque(),
        Deque().push(1),
        Deque().append(2),
        Deque().push(1).append(2),
    ]
)
def deque(request):
    return request.param


def test_that_pop_from_empty_deque_raises_an_exception(deque):
    if deque.empty():
        with pytest.raises(StackEmptyError):
            deque.pop()
    else:
        deque.pop()


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
        [1,2,3,4],
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
        range(0,len(deque)),
        populated_deque
    )

    for item in items:
        next_item = deque_without_prefilled_items.top()
        assert next_item is item
        deque_without_prefilled_items = deque_without_prefilled_items.pop()
