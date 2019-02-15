import pytest

from parsemon import character, fmap, run_parser
from parsemon.error import ParsingFailed
from parsemon.parser import many1
from parsemon.validator import even, odd


def test_even_validates_2():
    p = even.validates(
        fmap(
            lambda xs: int(''.join(xs)),
            many1(character())
        )
    )
    assert run_parser(p, '2').value == 2


def test_even_does_not_validate_5():
    p = even.validates(
        fmap(
            lambda xs: int(''.join(xs)),
            many1(character())
        )
    )
    with pytest.raises(ParsingFailed):
        run_parser(p, '3')


def test_odd_does_validate_5():
    p = odd.validates(
        fmap(
            lambda xs: int(''.join(xs)),
            many1(character())
        )
    )
    assert run_parser(p, '5').value == 5


def test_odd_and_even_neither_validate_2_nor_5():
    p = (odd & even).validates(
        fmap(
            lambda xs: int(''.join(xs)),
            many1(character())
        )
    )
    with pytest.raises(ParsingFailed):
        run_parser(p, '2')
    with pytest.raises(ParsingFailed):
        run_parser(p, '5')


def test_odd_or_even_validates_2_and_5():
    p = (odd | even).validates(
        fmap(
            lambda xs: int(''.join(xs)),
            many1(character())
        )
    )
    assert run_parser(p, '2').value == 2
    assert run_parser(p, '5').value == 5
