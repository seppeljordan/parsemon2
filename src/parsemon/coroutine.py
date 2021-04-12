from functools import wraps

from parsemon.extensions import trampoline

from .extensions import result


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
        def _do_parser(stream, original_continuation):
            generator = f(*args, **kwargs)

            def do_continuation(progressed_stream, previous_parsing_result):
                if previous_parsing_result.is_failure():
                    return trampoline.Call(
                        original_continuation,
                        progressed_stream,
                        previous_parsing_result,
                    )
                try:
                    next_parser = generator.send(previous_parsing_result.value)
                    return trampoline.Call(
                        next_parser,
                        progressed_stream,
                        do_continuation,
                    )
                except StopIteration as stop:
                    return trampoline.Call(
                        original_continuation,
                        progressed_stream,
                        result.success(getattr(stop, "value", None)),
                    )

            initial_parser = generator.send(None)
            return trampoline.Call(
                initial_parser,
                stream,
                do_continuation,
            )

        return _do_parser

    return decorator
