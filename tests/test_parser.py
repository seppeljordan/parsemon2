import parsemon

def test_can_parse_single_char():
    assert parsemon.char('a').parse('a') == 'a'

def test_parse_wrong_char_returns_none():
    parser = parsemon.char('a')
    assert parser.parse('b') is None

def test_char_and_then_char_parses_two_character_string():
    parser = parsemon.char('a').and_then(
        lambda r: parsemon.char('b'))
    assert parser.parse('ab') is not None

def test_alternatives_of_two_characters_can_parse_both_possible_characters():
    parser = parsemon.alternatives(
        parsemon.char('a'),
        parsemon.char('b')
    )
    assert parser.parse('a') is not None
    assert parser.parse('b') is not None

def test_alternatives_of_two_characters_can_parse_nothing_else():
    parser = parsemon.alternatives(
        parsemon.char('a'),
        parsemon.char('b')
    )
    assert parser.parse('c') is None
