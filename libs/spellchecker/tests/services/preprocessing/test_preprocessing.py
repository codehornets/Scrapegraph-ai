import pytest

from src.services.preprocessing import remove_extra_characters


def test_remove_extra_characters():
    assert remove_extra_characters("a-b") == "a-b"
    assert remove_extra_characters("a..bc!") == "abc"
    assert remove_extra_characters("ab-cd") == "ab-cd"
