from src.services.preprocessing.languages.zh import normalize_zh_text


def to_upper_case(text):
    return text.upper()


def test_normalize_zh_text():
    # Test that function returns None when input is None
    assert normalize_zh_text(None) is None

    # Test that function returns empty string when input is empty
    assert normalize_zh_text("") == ""

    # Test that function returns text as is when text is not empty and rules are not specified
    assert normalize_zh_text("hello") == "hello"

    # Test that function returns original text when text is provided but keep is False in rules
    rules = [(to_upper_case, False)]
    assert normalize_zh_text("hello", rules) == "hello"
