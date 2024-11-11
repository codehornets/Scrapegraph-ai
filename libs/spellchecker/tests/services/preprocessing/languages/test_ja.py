from src.services.preprocessing.languages.ja import normalize_ja_text


def to_upper_case(text):
    return text.upper()


def test_normalize_ja_text():
    # Test that function returns None when input is None
    assert normalize_ja_text(None) is None

    # Test that function returns empty string when input is empty
    assert normalize_ja_text("") == ""

    # Test that function returns text as is when text is not empty and rules are not specified
    assert normalize_ja_text("hello") == "hello"

    # Test that function returns original text when text is provided but keep is False in rules
    rules = [(to_upper_case, False)]
    assert normalize_ja_text("hello", rules) == "hello"
