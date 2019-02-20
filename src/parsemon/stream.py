from functools import reduce

from attr import attrib, attrs, evolve

from .deque import Stack, deque_empty


@attrs
class CharacterStream:
    content = attrib()
    length = attrib()
    _position = attrib()

    @classmethod
    def from_string(cls, content):
        return cls(
            content=reduce(
                lambda stack, character: stack.push(character),
                reversed(content),
                Stack()
            ),
            length=len(content),
            position=0,
        )

    def next(self):
        top_value = self.content.top()
        return None if top_value is deque_empty else top_value

    def read(self):
        return (
            self.next(),
            evolve(
                self,
                content=self.content.pop(),
                length=(
                    self.length
                    if self.content.empty()
                    else self.length - 1
                ),
                position=(
                    self._position
                    if self.content.empty()
                    else self._position + 1
                )
            )
        )

    def __len__(self):
        return self.length

    def to_string(self):
        return ''.join(self.content)

    def position(self):
        return self._position


@attrs
class StringStream:
    content = attrib()
    _position = attrib()
    length = attrib()

    @classmethod
    def from_string(cls, content):
        return cls(
            content,
            position=0,
            length=len(content),
        )

    def __len__(self):
        return self.length - self._position

    def to_string(self):
        return self.content[self._position:]

    def read(self):
        if self:
            return (
                self.content[self._position],
                evolve(
                    self,
                    position=self._position+1,
                )
            )
        else:
            return (
                None,
                self
            )

    def next(self):
        if self._position < self.length:
            return self.content[self._position]
        else:
            return None

    def position(self):
        return self._position
