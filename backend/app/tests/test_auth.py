from app.utils.jwt import create_access_token, decode_token
from app.utils.security import hash_password, verify_password

def test_password_hashing():
    pwd = "secretpassword123"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed)
    assert not verify_password("wrongpass", hashed)

def test_jwt_encoding_decoding():
    data = {"sub": "user_test_123", "email": "test@growthos.com"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_test_123"
