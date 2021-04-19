from parsemon import literal, parse_file


def test_can_open_file_and_run_a_parser(file_generator):
    test_file_path = file_generator.create_file(content="abcde")
    with open(test_file_path) as input_file:
        result = parse_file(literal("abcde"), input_file)
    assert result.value == "abcde"
