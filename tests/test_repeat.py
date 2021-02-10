from parsemon import literal, repeat, run_parser


def test_repeat_can_handle_1_repitition():
    text = "a"
    parser = repeat(literal("a"), 1)
    result = run_parser(parser, text)
    assert result.remaining_input == ""
    assert result.value == ["a"]


def test_repeat_can_handle_5_repitition():
    text = "aaaaa"
    parser = repeat(literal("a"), 5)
    result = run_parser(parser, text)
    assert result.remaining_input == ""
    assert result.value == ["a"] * 5
