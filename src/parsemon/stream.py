from __future__ import annotations

import io
from abc import ABC, abstractmethod
from typing import Optional

from attr import attrib, attrs


class Stream(ABC):
    @classmethod
    @abstractmethod
    def from_string(the_class, content):
        raise NotImplementedError()

    @abstractmethod
    def next(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def to_string(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def position(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def read(self) -> Optional[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_reset_point(self) -> ResetPoint:
        raise NotImplementedError()

    @abstractmethod
    def reset_stream(self, reset_point: ResetPoint) -> None:
        pass


class ResetPoint(ABC):
    @abstractmethod
    def destroy(self) -> None:
        pass


class StringStreamResetPoint(ResetPoint):
    def __init__(self, position) -> None:
        self.position = position

    def destroy(self) -> None:
        pass


@attrs
class StringStream(Stream):
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

    def to_string(self):
        return self.content[self._position :]

    def read(self):
        read_char = self.next()
        if read_char:
            self._position += 1
        return read_char

    def next(self):
        if self._position < self.length:
            return self.content[self._position]
        else:
            return None

    def position(self):
        return self._position

    def get_reset_point(self):
        return StringStreamResetPoint(self._position)

    def reset_stream(self, reset_point):
        self._position = reset_point.position


class IOStreamResetPoint(ResetPoint):
    def __init__(self, position):
        self.position = position

    def destroy(self):
        pass


@attrs
class IOStream(Stream):
    _stream = attrib()
    _position = attrib()
    _length = attrib()

    def next(self):
        self._stream.seek(self._position)
        character_read = self._stream.read(1)
        return character_read or None

    @classmethod
    def from_string(cls, message):
        return cls(
            stream=io.StringIO(message),
            position=0,
            length=len(message),
        )

    def read(self):
        self._stream.seek(self._position)
        character_read = self._stream.read(1)
        if character_read:
            self._position = self._stream.tell()
            return character_read
        else:
            return None

    def position(self):
        return self._position

    def to_string(self):
        return self._stream.read()

    def get_reset_point(self) -> IOStreamResetPoint:
        return IOStreamResetPoint(self._position)

    def reset_stream(self, reset_point) -> None:
        self._position = reset_point.position
