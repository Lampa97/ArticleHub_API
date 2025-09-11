from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    Model representing JWT access and refresh tokens.

    Attributes:
        access_token (str): The JWT access token for API authentication.
        refresh_token (str): The JWT refresh token for obtaining new access tokens.
    """
    access_token: str
    refresh_token: str

class TokenData(BaseModel):
    """
    Model for storing token payload data.

    Attributes:
        email (str): The email address extracted from the token's payload.
    """
    email: str

class User(BaseModel):
    """
    Model representing user registration and input data.

    Attributes:
        email (str): The user's email address.
        name (str): The user's display name.
        password (Optional[str]): The user's password (optional for public models).
    """
    email: str
    name: str
    password: Optional[str] = None

class UserInDB(User):
    """
    Model representing a user stored in the database.

    Inherits from User and adds:
        id (Optional[str]): The user's unique identifier in the database.
        hashed_password (str): The user's hashed password.
    """
    id: Optional[str] = None
    hashed_password: str

class UserPublic(BaseModel):
    """
    Model for returning public user profile information.

    Attributes:
        id (str): The user's unique identifier.
        email (str): The user's email address.
        name (str): The user's display name.
    """
    id: str
    email: str
    name: str
