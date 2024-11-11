from src.services.regex import get_ignore_patterns_for_language


def test_get_ignore_patterns_for_language():
    result = get_ignore_patterns_for_language("en_US")
    assert set(result) == {
        "\\b\\d{10}\\b",
        "pp-\\w+-\\d*",
        "[A-Za-z0-9]+/[A-Za-z0-9]+",
        "word\\d",
        "[^\x00-\x7f]+",
        "\\b[\\w-]+/[\\w-]+\\b",
        "\\b\\d{2}:\\d{2}:\\d{2}\\b",
        "\\b\\d{4}-\\d{2}-\\d{2}\\b",
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\\\(\\\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "\\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\\b",
    }

    result = get_ignore_patterns_for_language("undefined_language")
    assert set(result) == {
        "pp-\\w+-\\d*",
        "word\\d",
        "\\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\\b",
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\\\(\\\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "\\b\\d{4}-\\d{2}-\\d{2}\\b",
        "\\b\\d{2}:\\d{2}:\\d{2}\\b",
        "\\b\\d{10}\\b",
        "\\b[\\w-]+/[\\w-]+\\b",
        "[A-Za-z0-9]+/[A-Za-z0-9]+",
        "[^\x00-\x7f]+",
    }
