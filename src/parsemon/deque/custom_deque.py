from attr import attrib, attrs, evolve

from .empty import deque_empty
from .stack import Stack


@attrs
class Deque:
    front_stack = attrib(default=Stack())
    back_stack = attrib(default=Stack())

    def pop(self):
        if self.empty():
            return deque_empty
        if self.front_stack.empty():
            return evolve(
                self,
                back_stack=Stack(),
                front_stack=self.back_stack.flipped().pop()
            )
        else:
            return evolve(
                self,
                front_stack=self.front_stack.pop()
            )

    def push(self, value):
        return evolve(
            self,
            front_stack=self.front_stack.push(value)
        )

    def append(self, value):
        return evolve(
            self,
            back_stack=self.back_stack.push(value)
        )

    def top(self):
        if self.front_stack.empty():
            self.front_stack = self.back_stack.flipped()
            self.back_stack = Stack()
        return self.front_stack.top()

    def empty(self):
        return self.front_stack.empty() and self.back_stack.empty()

    def __len__(self):
        return len(self.front_stack) + len(self.back_stack)

    def last(self):
        return self.back_stack.top()

    def __iter__(self):
        yield from self.front_stack
        yield from reversed(self.back_stack)

    def flipped(self):
        return evolve(
            self,
            front_stack=self.back_stack,
            back_stack=self.front_stack,
        )

    def __reversed__(self):
        yield from self.flipped()
