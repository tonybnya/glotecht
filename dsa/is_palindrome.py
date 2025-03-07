"""
Task: Implement a function in Python that checks if a given string is a palindrome.
A palindrome is a string that reads the same forwards and backwards
(ignoring spaces, punctuation, and capitalization).
"""


def is_palindrome(s: str) -> bool:
     """
    Check if a string is a palindrome, ignoring non-alphabetic characters and case.

    Args:
        s: The input string to check.

    Returns:
        True if the string is a palindrome, False otherwise.
    """
    # Your code here
    i: int = 0
    j: int = len(s) - 1

    while i < j:
        if not s[i].isalpha():
            i += 1
            continue
        if not s[j].isalpha():
            j -= 1
            continue
        if s[i].lower() != s[j].lower():
            return False
        i += 1
        j -= 1

    return True