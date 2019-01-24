from parsemon.trampoline import Call, Result, with_trampoline


def test_trampoline_wraps_simple_functions():
    def f(x):
        return Result(x)
    assert with_trampoline(f)(1) == 1


def test_trampoline_wraps_tree_of_two_functions():
    def f(x):
        return Call(g, x)

    def g(x):
        return Result(x+1)

    assert with_trampoline(f)(1) == 2


def test_trampoline_wraps_factorial_function():
    def factorial(n, acc=1):
        if n < 2:
            return Result(acc)
        else:
            return Call(factorial, n - 1, acc * n)
    assert with_trampoline(factorial)(1000) is not None
