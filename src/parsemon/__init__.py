from typing import Any, Callable, Iterator, Tuple


class Parser(object):
    def __init__(
            self,
            consume_input: Callable[[str], Iterator[Tuple[Any, str]]]
    ) -> None:
        self.consume_input = consume_input

    def and_then(
            self,
            generate_next_parser: Callable[[Any],'Parser'],
    ):
        def consume(input_string):
            for result, input_rest in self.possible_results(input_string):
                next_parser = generate_next_parser(result)
                yield from next_parser.possible_results(input_rest)
        return Parser(consume)

    def possible_results(
            self,
            input_string: str
    ) -> Iterator[Tuple[Any,str]]:
        yield from self.consume_input(input_string)

    def parse(
            self,
            input_string: str
    ):
        for result in self.possible_results(input_string):
            if not result[1]:
                return result[0]
        return None


def char(character):
    def consume_input(s):
        if s[0] == character:
            yield (s,s[1:])
    return Parser(consume_input)


def alternatives(parser, alternative):
    def consume(s):
        yield from parser.possible_results(s)
        yield from alternative.possible_results(s)
    return Parser(consume)
