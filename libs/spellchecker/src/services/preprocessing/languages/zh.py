from functools import reduce

import stopwordsiso

CHINESE_STOPWORDS = stopwordsiso.stopwords(["zh"])


def normalize_zh_text(text, rules=None):
    if not text:
        return text

    def normalize(word, task):
        operation, keep = task
        return word if not keep else operation(word)

    return reduce(normalize, (), text.strip())
