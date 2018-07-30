from typing import Callable, Generic, Sized, Tuple, TypeVar

from .parser import Parser, bind, fail, unit

T = TypeVar('T')


class Validator(Generic[T]):
    def __init__(
            self,
            function: Callable[[T], Tuple[bool, str]]
    ) -> None:
        self.function = function

    def validates(
            self,
            parser: Parser[T, Sized]
    ) -> Parser[T, Sized]:

        def do_validation(
                to_validate: T,
        ) -> Parser[T, Sized]:
            is_validated, error_message = self.function(to_validate)
            if is_validated:
                return unit(to_validate)
            else:
                return fail(error_message)

        return bind(
            parser,
            do_validation
        )

    def __or__(self, other):
        def validator_function(value):
            self_result, self_error_msg = self.function(value)
            if self_result:
                return (self_result, self_error_msg)
            else:
                return other.function(value)
        return Validator(validator_function)

    def __and__(self, other):
        def validator_function(value):
            self_result, self_error = self.function(value)
            other_result, other_error = other.function(value)
            return (
                self_result and other_result,
                "{self_error} OR {other_error}".format(
                    self_error=self_error,
                    other_error=other_error,
                )
            )
        return Validator(validator_function)


even: Validator[int]
even = Validator(
    lambda n: (
        n % 2 == 0,
        'Expect even number but got {n}'.format(
            n=n
        )
    )
)


odd: Validator[int]
odd = Validator(
    lambda n: (
        n % 2 == 1,
        'Expected odd number but got {n}'.format(
            n=n
        )
    )
)
