from attr import attrib, attrs

from .empty import deque_empty

stack_bottom = object()


@attrs
class Stack():
    value = attrib(default=stack_bottom)
    next_elem = attrib(default=None)

    def empty(self):
        return self.value is stack_bottom

    def push(self, elem):
        return Stack(
            next_elem=self,
            value=elem
        )

    def top(self):
        if self.value == stack_bottom:
            return deque_empty
        else:
            return self.value

    def last(self):
        if self.empty():
            return deque_empty
        current_node = self
        while not current_node.next_elem.empty():
            current_node = current_node.pop()
        return current_node.value

    def pop(self):
        if self.empty():
            return deque_empty
        else:
            return self.next_elem

    def append(self, elem):
        accu = Stack().push(elem)
        for item in reversed(self):
            accu = accu.push(item)
        return accu

    def __iter__(self):
        i = self
        while not i.empty():
            yield i.value
            i = i.next_elem

    def __reversed__(self):
        yield from self.flipped()

    def __len__(self):
        length = 0
        iterator = self
        while not iterator.empty():
            length += 1
            iterator = iterator.pop()
        return length

    def flipped(self):
        accu = Stack()
        for item in self:
            accu = accu.push(item)
        return accu
