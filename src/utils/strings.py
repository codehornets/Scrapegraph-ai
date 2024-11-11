import random
import string


def generate_random_string(length=8):
    """Generate a random string of specified length (default is 8)."""
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))
