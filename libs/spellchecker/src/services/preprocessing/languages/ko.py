from functools import reduce

import stopwordsiso

KOREAN_STOPWORDS = stopwordsiso.stopwords(["ko"])


def normalize_ko_text(text, rules=None):
    if not text:
        return text

    def normalize(word, task):
        operation, keep = task
        return word if not keep else operation(word)

    return reduce(normalize, (), text.strip())
