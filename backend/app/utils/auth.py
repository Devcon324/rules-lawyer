import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security scheme
# Configured per RFC 6750: tokens passed in Authorization header as "Bearer <token>"
# auto_error=True ensures proper 401 responses with WWW-Authenticate header when token is missing
security = HTTPBearer(scheme_name="Bearer", auto_error=True)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify and decode a JWT token.
    
    Follows RFC 6750 Bearer Token Usage specification:
    - Tokens are passed in Authorization header as: Authorization: Bearer <token>
    - Error responses include WWW-Authenticate header with error codes
    """
    token = credentials.credentials
    
    # RFC 6750 compliant error responses
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="The access token is invalid"'},
    )
    
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication credentials expired",
        headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="The access token expired"'},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise invalid_token_exception
        return {"username": username, "payload": payload}
    except ExpiredSignatureError:
        raise expired_token_exception
    except JWTError:
        raise invalid_token_exception


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user against environment variables."""
    correct_username = secrets.compare_digest(
        username, os.getenv("AUTH_USERNAME", "")
    )
    correct_password = secrets.compare_digest(
        password, os.getenv("AUTH_PASSWORD", "")
    )
    return correct_username and correct_password

