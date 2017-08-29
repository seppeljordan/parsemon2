import pytest
from parsemon.stack import Stack, StackEmptyError


def test_new_stack_is_empty():
    assert Stack().empty()


def test_when_we_add_elem_to_stack_it_is_not_empty():
    assert not Stack().push('a').empty()


def test_when_we_push_an_elem_and_then_top_we_get_the_same_elem():
    value = 'a'
    assert Stack().push('a').top() == value


def test_top_on_empty_stack_raises_an_StackEmptyError():
    with pytest.raises(StackEmptyError):
        Stack().top()

def test_when_we_push_and_pop_we_get_the_empty_stack():
    assert Stack().push('a').pop().empty()

def test_pop_on_empty_stack_raises_StackEmptyError():
    with pytest.raises(StackEmptyError):
        Stack().pop()


def test_iterating_over_stack_sees_pushed_elems_in_reverse():
    elems = [1,2,3]
    s = Stack()
    for e in elems:
        s = s.push(e)
    elems.reverse()
    assert list(s) == elems
