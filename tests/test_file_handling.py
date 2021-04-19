from pytest import raises

from parsemon import FileTooLarge, literal, many, parse_file


def test_can_open_file_and_run_a_parser(file_generator):
    test_file_path = file_generator.create_file(content="abcde")
    with open(test_file_path) as input_file:
        result = parse_file(literal("abcde"), input_file)
    assert result.value == "abcde"


def test_raise_an_exception_if_file_size_is_larger_then_allowed(file_generator):
    test_file_path = file_generator.create_file(content="a" * 1000)
    with open(test_file_path) as input_file:
        with raises(FileTooLarge):
            parse_file(many(literal("a")), input_file, max_size=500)
