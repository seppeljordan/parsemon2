from functools import wraps
from typing import Callable, Generic, TypeVar
import abc

T = TypeVar('T')


class Trampoline(Generic[T], metaclass=abc.ABCMeta):

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def is_result(self):
        pass

    @abc.abstractmethod
    def __call__(self):
        pass


class Result(Trampoline, Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def is_result(self):
        return True

    def __call__(self):
        return self.value


class Call(Trampoline, Generic[T]):
    def __init__(
            self,
            f: Callable[..., T],
            *args,
            **kwargs
    ) -> None:
        self.fun = f
        self.args = args
        self.kwargs = kwargs

    def is_result(self):
        return False

    def __call__(self):
        return self.fun(*(self.args), **(self.kwargs))


def with_trampoline(f: Callable[..., Trampoline[T]]) -> Callable[..., T]:
    @wraps(f)
    def g(*args, **kwargs):
        iteration_result = f(*args, **kwargs)
        while True:
            if iteration_result.is_result():
                return iteration_result()
            else:
                iteration_result = iteration_result()
    return g
