from parsemon import do, floating_point, integer, run_parser


def test_if_integer_parses_1_digit():
    assert run_parser(integer(), '1') == 1


def test_if_integer_parses_2_digits():
    assert run_parser(integer(), '42') == 42


def test_if_integer_parses_negative_numbers():
    assert run_parser(integer(), '-987') == -987


def test_if_integer_parses_plus_prefix():
    assert run_parser(integer(), '+132') == 132


def test_if_floating_point_parses_simple_integer():
    assert run_parser(floating_point(), '1') == float(1)


def test_if_floating_point_parses_number_with_one_point_in_the_middle():
    assert run_parser(floating_point(), '1.1') == 1.1


def test_if_floating_point_parses_number_without_integer_part():
    assert run_parser(floating_point(), '.1') == .1


def test_if_floating_point_parses_number_without_rational_part():
    assert run_parser(floating_point(), '1.') == 1.


def test_if_floating_point_recognizes_one_sign_before_number():
    assert run_parser(floating_point(), '+1.1') == +1.1
