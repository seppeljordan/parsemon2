from functools import wraps
from typing import Callable, Generic, TypeVar, Union

T = TypeVar("T")


class Result(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"<Result value={self.value}>"


class Call(Generic[T]):
    def __init__(self, f: Callable[..., T], *args, **kwargs) -> None:
        self.fun = f
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"<Call fun={self.fun} args={self.args} kwargs={self.kwargs}>"


Trampoline = Union[Result[T], Call[T]]


def with_trampoline(f: Callable[..., Trampoline[T]]) -> Callable[..., T]:
    @wraps(f)
    def g(*args, **kwargs):
        iteration_result = f(*args, **kwargs)
        while True:
            if isinstance(iteration_result, Result):
                return iteration_result.value
            else:
                iteration_result = iteration_result.fun(
                    *iteration_result.args, **iteration_result.kwargs
                )

    return g
