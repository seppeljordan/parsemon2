from .parser import bind
from .parser import unit


def do(f):
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
