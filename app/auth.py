import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, Request
from .config import settings
from .database import get_user_by_id

ALGORITHM = "HS256"
TOKEN_MINUTES = 60 * 24

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
    return (
        "pbkdf2_sha256$210000$"
        + base64.urlsafe_b64encode(salt).decode()
        + "$"
        + base64.urlsafe_b64encode(digest).decode()
    )

def verify_password(password: str, encoded: str) -> bool:
    try:
        _, rounds, salt_b64, digest_b64 = encoded.split("$")
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def create_access_token(user_id: int):
    exp = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": exp}, settings.secret_key, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def current_user(request: Request):
    auth_header = request.headers.get("Authorization", "")
    token = request.cookies.get("access_token")
    if not token and auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = get_user_by_id(decode_token(token))
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user
