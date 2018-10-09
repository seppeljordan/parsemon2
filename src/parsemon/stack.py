from parsemon.trampoline import Call, Result, with_trampoline
from functools import reduce


class StackBottom(object):
    pass


class StackEmptyError(Exception):
    pass


stack_bottom = StackBottom()


class Stack():
    def __init__(self):
        self.value = stack_bottom
        self.next_elem = None

    def empty(self):
        return self.value is stack_bottom

    def push(self, elem):
        s = Stack()
        s.next_elem = self
        s.value = elem
        return s

    def top(self):
        if self.value == stack_bottom:
            raise StackEmptyError(
                'top on stack bottom not allowed'
            )
        else:
            return self.value

    def pop(self):
        if self.empty():
            raise StackEmptyError(
                'pop on empty stack is not allowed'
            )
        else:
            return self.next_elem

    def append(self, elem):
        def _reverse(rest, accu):
            if rest.empty():
                return Result(accu)
            else:
                return Call(
                    _reverse,
                    rest.pop(),
                    accu.push(rest.top()),
                )

        def reverse(s):
            return with_trampoline(_reverse)(s, Stack())
        return reverse(reverse(self).push(elem))

    def __iter__(self):
        i = self
        while not i.empty():
            yield i.value
            i = i.next_elem

    def __reversed__(self):
        yield from reversed(list(self))

    def flipped(self):
        return reduce(
            lambda accu, next: accu.push(next),
            self,
            Stack()
        )
