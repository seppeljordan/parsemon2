import pytest

from parsemon import ParsingFailed, floating_point, integer, run_parser


def test_if_integer_parses_1_digit():
    assert run_parser(integer(), '1').value == 1


def test_if_integer_parses_2_digits():
    assert run_parser(integer(), '42').value == 42


def test_if_integer_parses_negative_numbers():
    assert run_parser(integer(), '-987').value == -987


def test_if_integer_parses_plus_prefix():
    assert run_parser(integer(), '+132').value == 132


def test_if_floating_point_parses_simple_integer():
    assert run_parser(floating_point(), '1').value == float(1)


def test_if_floating_point_parses_number_with_one_point_in_the_middle():
    assert run_parser(floating_point(), '1.1').value == 1.1


def test_if_floating_point_parses_number_without_integer_part():
    assert run_parser(floating_point(), '.1').value == .1


def test_if_floating_point_parses_number_without_rational_part():
    assert run_parser(floating_point(), '1.').value == 1.


def test_if_floating_point_recognizes_one_sign_before_number():
    assert run_parser(floating_point(), '+1.1').value == +1.1


def test_if_floating_point_recognizes_custom_delimiters():
    assert run_parser(floating_point(delimiter=','), '123,12').value == 123.12


def test_if_floating_point_recognizes_custom_delimiters_without_integer_part():
    assert run_parser(floating_point(delimiter=','), '-,2').value == -.2


def test_if_floating_point_recognizes_float_with_e_notation():
    assert run_parser(floating_point(), '1e1').value == 1e1


def test_that_floating_point_does_not_recognize_number_without_rational_part():
    with pytest.raises(ParsingFailed):
        run_parser(floating_point(), '.e1')
