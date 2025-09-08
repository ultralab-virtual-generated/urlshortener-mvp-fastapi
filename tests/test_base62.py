from app.utils.base62 import generate_code, ALPHABET

def test_generate_code_length_and_charset():
    code = generate_code(6)
    assert len(code) == 6
    assert all(ch in ALPHABET for ch in code)
