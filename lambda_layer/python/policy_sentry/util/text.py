"""
Methods that are basically text/string operations for specific purposes
"""


def capitalize_first_character(some_string: str) -> str:
    """
    Description: Capitalizes the first character of a string
    :param some_string:
    :return:
    """
    return " ".join("".join([w[0].upper(), w[1:].lower()]) for w in some_string.split())


def strip_special_characters(some_string: str) -> str:
    """Remove all special characters, punctuation, and spaces from a string"""
    # Input: "Special $#! characters   spaces 888323"
    # Output: 'Specialcharactersspaces888323'
    return "".join(e for e in some_string if e.isalnum())
