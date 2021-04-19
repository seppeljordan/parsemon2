"""This module contains parser specific exceptions"""


class ParsingFailed(Exception):
    """Base exception class for all possible ways a parser can fail"""

    pass


class FileTooLarge(Exception):
    """The file to be parsed is larger then the specified limit."""
