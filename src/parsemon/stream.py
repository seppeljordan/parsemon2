from __future__ import annotations

import io
from abc import ABC, abstractmethod
from typing import Optional


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


class StringStream(Stream):
    def __init__(self, content: str, position: int):
        self.content = content
        self._position = position

    @classmethod
    def from_string(cls, content):
        return cls(
            content,
            position=0,
        )

    def to_string(self):
        return self.content[self._position :]

    def read(self):
        read_char = self.next()
        if read_char:
            self._position += 1
        return read_char

    def next(self):
        try:
            return self.content[self._position]
        except IndexError:
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


class IOStream(Stream):
    def __init__(self, stream):
        self._peeked_char = None
        self._stream = stream

    def next(self):
        self._peeked_char = self.read()
        return self._peeked_char

    @classmethod
    def from_string(cls, message):
        return cls(
            stream=io.StringIO(message),
        )

    def read(self):
        if self._peeked_char:
            result = self._peeked_char
            self._peeked_char = None
            return result
        else:
            return self._stream.read(1) or None

    def position(self):
        return self._stream.tell() + (-1 if self._peeked_char else 0)

    def to_string(self):
        return self._stream.read()

    def get_reset_point(self) -> IOStreamResetPoint:
        return IOStreamResetPoint(self.position())

    def reset_stream(self, reset_point) -> None:
        self._stream.seek(reset_point.position)
