
import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import models
from database import get_db


# JWT configuration
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret-key-change-before-production"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
password_hash = PasswordHash.recommended()

# Extracts the Bearer token from incoming requests
oauth2_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password before storing it in the database."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Check whether a password matches its stored hash."""
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Create a JWT token for an authenticated user."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    """Identify the user from the JWT token."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired login token.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None or not user.is_active:
        raise credentials_exception

    return user
