from attr import attrib, attrs, evolve

from .stack import Stack, StackEmptyError


@attrs
class Deque:
    front_stack = attrib(default=Stack())
    back_stack = attrib(default=Stack())

    def pop(self):
        if self.empty():
            raise StackEmptyError()
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
        return (
            self.back_stack.flipped().top()
            if self.front_stack.empty()
            else self.front_stack.top()
        )

    def empty(self):
        return self.front_stack.empty() and self.back_stack.empty()

    def __len__(self):
        return len(self.front_stack) + len(self.back_stack)

    def last(self):
        return self.back_stack.top()

    def __iter__(self):
        yield from self.front_stack
        yield from self.front_stack.flipped()

    def flipped(self):
        return evolve(
            self,
            front_stack=self.back_stack,
            back_stack=self.front_stack,
        )

    def __reversed__(self):
        yield from self.flipped()
