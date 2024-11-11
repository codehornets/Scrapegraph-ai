from functools import reduce

import stopwordsiso

JAPANESE_STOPWORDS = stopwordsiso.stopwords(["ja"])


def normalize_ja_text(text, rules=None):
    if not text:
        return text

    def normalize(word, task):
        operation, keep = task
        return word if not keep else operation(word)

    return reduce(normalize, (), text.strip())
