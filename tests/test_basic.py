from parsemon import run_parser
from parsemon import integer


def test_if_integer_parses_1_digit():
    assert run_parser(integer, '1') == 1


def test_if_integer_parses_2_digits():
    assert run_parser(integer, '42') == 42


def test_if_integer_parses_negative_numbers():
    assert run_parser(integer, '-987') == -987


def test_if_integer_parses_plus_prefix():
    assert run_parser(integer, '+132') == 132
