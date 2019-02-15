import pytest

from parsemon import ParsingFailed, run_parser
from parsemon.json import (json_bool, json_document, json_list, json_null,
                           json_number, json_object, json_string)


def test_json_string_parses_abc_as_intended():
    assert run_parser(json_string(), '"abc"').value == "abc"


def test_json_string_can_handle_escaped_quotes():
    assert run_parser(json_string(), '"\\\""').value == '"'


def test_json_string_can_handle_escaped_chars():
    assert (
        run_parser(json_string(), '"\\"\\f\\b\\n\\r\\\\\\t"').value ==
        '\"\f\b\n\r\\\t'
    )


def test_json_string_can_handle_unicode_escapes():
    assert run_parser(json_string(), '"\\u003d"').value == '='


def test_json_number_can_handle_0_string():
    assert run_parser(json_number(), '0').value == 0


def test_json_number_can_handle_two_digit_string():
    assert run_parser(json_number(), '45').value == 45


def test_json_number_raises_with_leading_zero():
    with pytest.raises(ParsingFailed):
        run_parser(json_number(), '01')


def test_json_number_can_handle_leading_minus():
    run_parser(json_number(), '-1').value == -1


def test_json_number_can_handle_floats():
    run_parser(json_number(), '1.1').value == 1.1


def test_json_number_raises_when_period_without_fraction():
    with pytest.raises(ParsingFailed):
        run_parser(json_number(), '1.')


def test_json_number_can_handle_exponents():
    assert run_parser(json_number(), '1e+0').value == float('1e+0')


def test_json_number_can_handle_negative_exponents():
    assert (
        run_parser(json_number(), '1.54e-2').value ==
        float('1.54e-2')
    )


def test_json_bool_detects_true():
    assert run_parser(json_bool(), 'true').value


def test_json_bool_detects_false():
    assert not run_parser(json_bool(), 'false').value


def test_json_bool_fails_on_other_strings():
    with pytest.raises(ParsingFailed):
        run_parser(json_bool(), 'abcd')


def test_json_null_detects_null():
    assert run_parser(json_null(), 'null').value is None


def test_json_null_fails_on_other_strings():
    with pytest.raises(ParsingFailed):
        run_parser(json_null(), 'abcd')


def test_json_list_parses_empty_list():
    assert run_parser(json_list(), '[]').value == []


def test_json_list_parses_empty_list_with_5_spaces():
    assert run_parser(json_list(), '[     ]').value == []


def test_json_list_parses_list_with_one_int_in_it():
    assert run_parser(json_list(), '[1]').value == [1]


def test_json_list_parses_a_list_of_2_ints():
    assert run_parser(json_list(), '[1,2]').value == [1, 2]


def test_json_list_parses_list_including_spaces():
    assert run_parser(json_list(), '[1,  2 ,3]').value == [1, 2, 3]


def test_json_list_parses_list_of_strings_and_ints():
    assert (
        run_parser(json_list(), '[1, "two", 3, "four"]').value ==
        [1, "two", 3, "four"]
    )


def test_json_list_parses_a_list_with_null_in_it():
    assert run_parser(json_list(), '[ null ]').value == [None]


def test_json_list_handles_a_list_of_lists():
    assert (
        run_parser(json_list(), "[1, [2,3], [],[[]]]").value ==
        [1, [2, 3], [], [[]]]
    )


def test_json_object_parses_empty_object():
    assert run_parser(json_object(), '{}').value == {}


def test_json_object_parses_empty_object_with_spaces():
    assert run_parser(json_object(), '{     }').value == {}


def test_json_object_parses_object_with_one_entry():
    assert run_parser(json_object(), '{"a": 1}').value == {'a': 1}


def test_json_object_parses_object_with_object_inside():
    assert (
        run_parser(json_object(), '{"a": {"b": {}}}').value ==
        {'a': {'b': {}}}
    )


def test_json_value_parses_bool_value():
    assert run_parser(json_object(), '{"a":true}').value == {'a': True}


def test_json_document_trims_whitespaces():
    assert run_parser(json_document(), ' {}  ').value == {}
