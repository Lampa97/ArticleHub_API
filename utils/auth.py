from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from models.auth import TokenData, User, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")


def verify_password(plain_password, hashed_password):
    """
    Verify that a plain password matches its hashed version.

    Args:
        plain_password (str): The plain text password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hash a plain password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


async def get_user(users_collection, email: str):
    """
    Retrieve a user document from the database by email.

    Args:
        users_collection: The MongoDB collection for users.
        email (str): The email address of the user to retrieve.

    Returns:
        UserInDB | None: The user object if found, otherwise None.
    """
    user_dict = await users_collection.find_one({"email": email})
    if user_dict:
        user_dict["id"] = str(user_dict["_id"])
        user_dict.pop("_id")
        return UserInDB(**user_dict)


async def authenticate_user(users_collection, email: str, password: str):
    """
    Authenticate a user by verifying their email and password.

    Args:
        users_collection: The MongoDB collection for users.
        email (str): The user's email address.
        password (str): The user's plain text password.

    Returns:
        UserInDB | bool: The authenticated user object, or False if authentication fails.
    """
    user = await get_user(users_collection, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token for authentication.

    Args:
        data (dict): The payload data to encode in the token.
        expires_delta (timedelta, optional): The token's expiration time. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Retrieve the current authenticated user based on the JWT token.

    Args:
        request (Request): The FastAPI request object.
        token (str): The JWT token provided by the client.

    Raises:
        HTTPException: If the token is invalid or the user cannot be found.

    Returns:
        UserInDB: The authenticated user object.
    """
    users_collection = request.app.mongodb["users"]
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(users_collection, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Dependency to retrieve the current active user.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        User: The current active user.
    """
    return current_user
