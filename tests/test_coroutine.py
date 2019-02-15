from parsemon import chain, choice, literal, run_parser, try_parser
from parsemon.coroutine import do


def test_can_combine_2_parsers_with_do():
    @do
    def a_and_b():
        first = yield literal('a')
        second = yield literal('b')
        return first + second

    assert run_parser(a_and_b(), 'ab').value == 'ab'


def test_can_use_do_notation_in_choice():
    @do
    def a_and_b():
        a = yield literal('a')
        b = yield literal('b')
        return a + b

    p = choice(
        try_parser(chain(
            a_and_b(),
            literal('a')
        )),
        try_parser(chain(
            a_and_b(),
            literal('b')
        ))
    )

    assert run_parser(p, 'aba').value == 'a'
    assert run_parser(p, 'abb').value == 'b'


def test_do_can_handle_1000_parsers_combined_in_one_do_block():
    @do
    def a_10000_times():
        for n in range(0, 1000):
            yield literal('a')
        return True

    assert run_parser(a_10000_times(), 'a' * 1000).value


def test_do_can_handle_parameters_correctly():
    @do
    def a_for_n_times(n):
        for _ in range(0, n):
            yield literal('a')
        return True

    assert run_parser(a_for_n_times(5), 'a' * 5).value


def test_that_do_can_handle_parsers_that_do_not_return_anything():
    @do
    def trivial():
        yield literal('a')
    assert run_parser(trivial(), 'a').value is None


def test_that_parsers_with_do_notation_can_excecute_twice_with_same_result():
    @do
    def trivial():
        yield literal('a')
    parser = trivial()

    def is_success():
        return run_parser(parser, 'a').value is None

    assert is_success()
    assert is_success()
