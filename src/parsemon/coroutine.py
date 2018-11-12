from functools import wraps

from .parser import bind, unit


def do(f):
    """Use this as a decorator

    Do allows you to combine parsers in a more pythonic way.

    It expects a generator that returns something in the end and takes
    no arguments.

    It lets you write parsers like the following::

        @do
        def three_letters():
            first = yield character()
            second = yield character()
            third = yield character()
            return first + second + third

    """
    @wraps(f)
    def decorator(*args, **kwargs):
        generator = f(*args, **kwargs)

        def inner(value, parser=None):
            try:
                next_parser = parser.send(value)
            except StopIteration as stop:
                return unit(
                    getattr(stop, 'value', None)
                )
            else:
                return bind(
                    next_parser,
                    lambda next_value: inner(next_value, parser)
                )

        return inner(None, generator)

    return decorator
