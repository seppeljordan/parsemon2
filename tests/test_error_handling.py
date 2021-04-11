from pytest import raises

from parsemon import do, run_parser, unit


def test_attribute_errors_are_propagated_correctly():
    @do
    def parser():
        yield unit(True)
        {}.a  # this is an intentional attribute error
        yield unit(True)
        return True

    with raises(AttributeError) as error:
        run_parser(parser(), "")
    assert str(error.value) == "'dict' object has no attribute 'a'"
