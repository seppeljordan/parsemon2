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
        return self.value == stack_bottom

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

    def __iter__(self):
        i = self
        while not i.empty():
            yield i.value
            i = i.next_elem
