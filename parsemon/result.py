"""This module is concerned with the results of a parser."""

from abc import ABC, abstractmethod
from typing import Callable, Generic, List, TypeVar, Union, cast

from attr import attrib, attrs, evolve

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class Result(ABC, Generic[T, U]):
    @abstractmethod
    def is_failure(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def map_value(self, mapping: Callable[[T], V]) -> "Result[V,U]":
        raise NotImplementedError()


@attrs
class Success(Result[T, U]):
    value: T = attrib()

    def map_value(self, mapping: Callable[[T], V]) -> "Result[V,U]":
        return evolve(
            cast(Result[V, U], self),
            value=mapping(self.value),
        )

    def is_failure(self) -> bool:
        return False


@attrs
class Failure(Result[T, U]):
    message: U = attrib()
    position: int = attrib()

    def map_value(self, mapping: Callable[[T], V]) -> "Result[V,U]":
        return cast(Result[V, U], self)

    def __add__(self, other: "Union[Failure[T,U], Failures[T,U]]") -> "Result[T,U]":
        if isinstance(other, Failures):
            return evolve(other, failures=[self] + other.failures)
        elif isinstance(other, Failure):
            return Failures(failures=[self, other])
        else:
            return NotImplemented

    def is_failure(self) -> bool:
        return True


@attrs
class Failures(Result[T, U]):
    failures: List[Failure[T, U]] = attrib()

    def __add__(self, other):
        other_failures = other.failures if isinstance(other, Failures) else [other]
        return Failures(failures=self.failures + other_failures)

    def map_value(self, mapping: Callable[[T], V]) -> "Failures[V,U]":
        return cast(Failures[V, U], self)

    def is_failure(self) -> bool:
        return True


def failure(message, position):
    return Failure(
        message=message,
        position=position,
    )


def success(value):
    return Success(value)


@attrs
class ParsingResult:
    value = attrib()
    remaining_input = attrib()


def parsing_result(value, remaining_input):
    return ParsingResult(value, remaining_input)
