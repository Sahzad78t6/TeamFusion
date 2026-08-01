import bcrypt


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using native bcrypt.
    Safely truncates to 72 bytes as required by bcrypt specification.
    """
    if not password:
        password = ""
    pwd_bytes = str(password).encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash safely.
    """
    try:
        if not plain_password or not hashed_password:
            return False
        pwd_bytes = str(plain_password).encode("utf-8")[:72]
        hash_bytes = str(hashed_password).encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False
