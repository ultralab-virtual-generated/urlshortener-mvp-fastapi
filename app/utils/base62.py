import secrets
import string

ALPHABET = string.digits + string.ascii_letters  # 0-9a-zA-Z


def generate_code(length: int = 6) -> str:
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))
