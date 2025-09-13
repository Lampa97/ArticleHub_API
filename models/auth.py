from typing import Optional

from pydantic import BaseModel, EmailStr, ValidationError, field_validator


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

    email: EmailStr
    name: str
    password: Optional[str] = None

    @field_validator("name")
    def name_no_spaces(cls, name):
        if " " in name:
            raise ValueError("Name must not contain spaces")
        return name

    @field_validator("password")
    def password_strength(cls, password):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one digit")
        if not any(c.isalpha() for c in password):
            raise ValidationError("Password must contain at least one letter")
        return password


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
    email: EmailStr
    name: str
