"""This module contains parser specific exceptions"""


class ParsingFailed(Exception):
    """Base exception class for all possible ways a parser can fail"""
    pass


class NotEnoughInput(ParsingFailed):
    """Parser failed because not enough input was present.

    This exception denotes that a parser failed because there was not enough
    input to consume.
    """
    pass
