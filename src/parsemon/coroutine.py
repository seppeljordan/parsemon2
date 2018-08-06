from .parser import bind
from .parser import unit


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
    class StartIteration:
        pass

    def inner(value, parser=None):
        if value is StartIteration:
            parser = f()
            value = None
        try:
            next_parser = parser.send(value)
        except StopIteration as e:
            return unit(e.args[0])
        else:
            return bind(
                next_parser,
                lambda next_value: inner(next_value, parser)
            )

    return bind(
        unit(StartIteration),
        inner
    )
