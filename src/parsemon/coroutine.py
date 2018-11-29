from functools import wraps

from .internals import unit


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
        def inner(value, generator=None):
            if generator is None:
                generator = f(*args, **kwargs)
            try:
                next_parser = generator.send(value)
            except StopIteration as stop:
                return unit(
                    getattr(stop, 'value', None)
                )
            else:
                return next_parser.bind(
                    lambda next_value: inner(next_value, generator)
                )

        return unit(None).bind(inner)

    return decorator
