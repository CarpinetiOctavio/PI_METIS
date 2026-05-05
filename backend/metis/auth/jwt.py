import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload["exp"] = expire
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])


def is_valid_token(token: str) -> dict | None:
    try:
        return decode_access_token(token)
    except JWTError:
        return None
