"""
admin JWT authentication: password-based login issues a short-lived JWT used for destructive operations.
"""
import os
import jwt
import datetime
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
JWT_SECRET     = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM  = "HS256"
JWT_EXPIRE_H   = 24  # token lifetime in hours

bearer_scheme = HTTPBearer(auto_error=False)


def create_admin_token() -> str:
    """issue a signed JWT valid for JWT_EXPIRE_H hours."""
    payload = {
        "sub": "admin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRE_H),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """FastAPI dependency — raises 401 if the Bearer token is missing, expired or invalid."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Přihlášení vyžadováno.")
    try:
        jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Přihlášení vypršelo, přihlaste se znovu.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Neplatný token.")
