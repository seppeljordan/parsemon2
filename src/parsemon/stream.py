from __future__ import annotations

import io
from abc import ABC, abstractmethod
from typing import Optional, TextIO


class Stream(ABC):
    @classmethod
    @abstractmethod
    def from_string(the_class, content: str) -> Stream:
        raise NotImplementedError()

    @abstractmethod
    def next(self) -> Optional[str]:
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

    @abstractmethod
    def get_position(self) -> int:
        pass


class StringStreamResetPoint(ResetPoint):
    def __init__(self, position: int) -> None:
        self.position = position

    def destroy(self) -> None:
        pass

    def get_position(self) -> int:
        return self.position


class StringStream(Stream):
    def __init__(self, content: str, position: int) -> None:
        self.content = content
        self._position = position

    @classmethod
    def from_string(cls, content: str) -> StringStream:
        return cls(
            content,
            position=0,
        )

    def to_string(self) -> str:
        return self.content[self._position :]

    def read(self) -> Optional[str]:
        read_char = self.next()
        if read_char:
            self._position += 1
        return read_char

    def next(self) -> Optional[str]:
        try:
            return self.content[self._position]
        except IndexError:
            return None

    def position(self) -> int:
        return self._position

    def get_reset_point(self) -> StringStreamResetPoint:
        return StringStreamResetPoint(self._position)

    def reset_stream(self, reset_point: ResetPoint) -> None:
        self._position = reset_point.get_position()


class IOStreamResetPoint(ResetPoint):
    def __init__(self, position: int):
        self.position = position

    def destroy(self) -> None:
        pass

    def get_position(self) -> int:
        return self.position


class IOStream(Stream):
    def __init__(self, stream: TextIO):
        self._peeked_char: Optional[str] = None
        self._stream = stream

    def next(self) -> Optional[str]:
        self._peeked_char = self.read()
        return self._peeked_char

    @classmethod
    def from_string(cls, content: str) -> IOStream:
        return cls(
            stream=io.StringIO(content),
        )

    def read(self) -> Optional[str]:
        if self._peeked_char:
            result = self._peeked_char
            self._peeked_char = None
            return result
        else:
            return self._stream.read(1) or None

    def position(self) -> int:
        return self._stream.tell() + (-1 if self._peeked_char else 0)

    def to_string(self) -> str:
        result: str = ""
        if self._peeked_char:
            result = self._peeked_char
        return result + self._stream.read()

    def get_reset_point(self) -> IOStreamResetPoint:
        return IOStreamResetPoint(self.position())

    def reset_stream(self, reset_point: ResetPoint) -> None:
        self._stream.seek(reset_point.get_position())
