import re


def remove_extra_characters_and_digits(s):
    # Find the last character in the string that is a letter
    last_alpha = max((loc for loc, char in enumerate(s) if char.isalpha()), default=-1)

    # Now check if there's a non-alphabetic character after this
    match = re.search(r"\W", s[last_alpha + 1 :])  # noqa: E203

    # If there is, remove everything from that point forward
    if match:
        return s[: last_alpha + 1]

    # If there is no special character after the final letter, but there is a digit
    last_digit = max((loc for loc, char in enumerate(s) if char.isdigit()), default=-1)
    if last_digit > last_alpha:
        return s[: last_alpha + 1]

    return s
