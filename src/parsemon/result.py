"""This module is concerned with the results of a parser."""

from attr import attrib, attrs, evolve


@attrs
class Success:
    value = attrib()
    stream = attrib()

    def map_value(self, mapping):
        return evolve(
            self,
            value=mapping(self.value),
        )

    def is_failure(_):
        return False

    def map_stream(self, mapping):
        return evolve(
            self,
            stream=mapping(self.stream)
        )

    def remaining_input(self):
        return self.stream.to_string()


@attrs
class Failure:
    message = attrib()
    stream = attrib()

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

    def last_stream(self):
        return self.stream

    def is_failure(_):
        return True

    def map_stream(self, mapping):
        return evolve(
            self,
            stream=mapping(self.stream)
        )


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

    def map_value(self, fun):
        return evolve(
            self,
            failures=list(map(
                lambda failure: failure.map_value(fun),
                self.failures
            ))
        )

    def last_stream(self):
        if self.failures:
            return self.failures[-1].stream
        else:
            return None

    def is_failure(_):
        return True

    def map_stream(self, mapping):
        return evolve(
            self,
            failures=list(map(
                lambda f: f.map_stream(mapping),
                self.failures
            ))
        )


def failure(message, stream):
    return Failure(
        message=message,
        stream=stream,
    )


def success(value, stream):
    return Success(value, stream)
