from attr import attrib, attrs, evolve
from pyrsistent import pdeque

from .empty import deque_empty


@attrs
class PyrsistentDeque:
    deque = attrib(default=pdeque())

    def pop(self):
        if self.empty():
            return deque_empty
        return evolve(
            self,
            deque=self.deque.popleft()
        )

    def push(self, value):
        return evolve(
            self,
            deque=self.deque.appendleft(value)
        )

    def append(self, value):
        return evolve(
            self,
            deque=self.deque.append(value)
        )

    def top(self):
        if self.empty():
            return deque_empty
        return self.deque.left

    def empty(self):
        return not len(self.deque)

    def __len__(self):
        return len(self.deque)

    def last(self):
        if self.empty():
            return deque_empty
        return self.deque.right

    def __iter__(self):
        yield from self.deque

    def flipped(self):
        return evolve(
            self,
            deque=self.deque.reverse()
        )

    def __reversed__(self):
        yield from self.flipped()
