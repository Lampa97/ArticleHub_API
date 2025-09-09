from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    email: str


class User(BaseModel):
    email: str
    name: str
    password: Optional[str] = None


class UserInDB(User):
    id: Optional[str] = None
    hashed_password: str


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
