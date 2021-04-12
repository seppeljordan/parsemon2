from typing import Generic, TypeVar

from parsemon.extensions import trampoline

from .internals import fail
from .parser import bind, unit

T = TypeVar("T")


class Validator(Generic[T]):
    def __init__(self, function) -> None:
        self.function = function

    def validates(
        self,
        parser,
    ):
        def do_validation(
            to_validate: T,
        ):
            is_validated, error_message = trampoline.with_trampoline(
                self.function, to_validate
            )
            if is_validated:
                return unit(to_validate)
            else:
                return fail(error_message)

        return bind(parser, do_validation)

    def __or__(self, other):
        def validator_function(value):
            self_result, self_error_msg = trampoline.with_trampoline(
                self.function, value
            )
            if self_result:
                return trampoline.Result((self_result, self_error_msg))
            else:
                return trampoline.Call(other.function, value)

        return Validator(validator_function)

    def __and__(self, other):
        def validator_function(value):
            self_result, self_error = trampoline.with_trampoline(self.function, value)
            other_result, other_error = trampoline.with_trampoline(
                other.function, value
            )
            return trampoline.Result(
                (
                    self_result and other_result,
                    "{self_error} OR {other_error}".format(
                        self_error=self_error,
                        other_error=other_error,
                    ),
                )
            )

        return Validator(validator_function)


even: Validator[int]
even = Validator(
    lambda n: trampoline.Result(
        (n % 2 == 0, "Expect even number but got {n}".format(n=n))
    )
)


odd: Validator[int]
odd = Validator(
    lambda n: trampoline.Result(
        (n % 2 == 1, "Expected odd number but got {n}".format(n=n))
    )
)
