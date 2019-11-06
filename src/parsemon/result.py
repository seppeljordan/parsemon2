"""This module is concerned with the results of a parser."""

from attr import attrib, attrs, evolve


@attrs
class Success:
    value = attrib()

    def map_value(self, mapping):
        return evolve(
            self,
            value=mapping(self.value),
        )

    def is_failure(_):
        return False


@attrs
class Failure:
    message = attrib()
    position = attrib()

    def map_value(self, _):
        return self

    def __add__(self, other):
        if isinstance(other, Failures):
            return evolve(
                other,
                failures=[self] + other.failures
            )
        return Failures(
            failures=[
                self,
                other
            ]
        )

    def is_failure(_):
        return True


@attrs
class Failures:
    failures = attrib()

    def __add__(self, other):
        other_failures = (
            other.failures
            if isinstance(other, Failures)
            else [other]
        )
        return Failures(
            failures=self.failures + other_failures
        )

    def map_value(self, _):
        return self

    def is_failure(_):
        return True


def failure(message, position):
    return Failure(
        message=message,
        position=position,
    )


def success(value):
    return Success(value)


@attrs
class ParsingResult():
    value = attrib()
    remaining_input = attrib()


def parsing_result(value, remaining_input):
    return ParsingResult(value, remaining_input)
