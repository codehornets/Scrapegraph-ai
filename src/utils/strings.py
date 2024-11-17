import random
import re
import string

from stopwordsiso import stopwords

from src.utils.debug import die


def generate_random_string(length=8):
    """Generate a random string of specified length (default is 8)."""
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def preprocess_value(value: str) -> str:
    value = value.lower().strip()

    # Remove punctuation
    value = re.sub(r"[^\w\s]", "", value)

    # Tokenize and remove duplicates
    tokens = list(dict.fromkeys(value.split()))

    # Optional: Remove stopwords
    tokens = [token for token in tokens if token not in stopwords("en")]

    # Join tokens back into a string
    return " ".join(tokens)
