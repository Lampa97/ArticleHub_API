from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from models.auth import Token, User, UserInDB, UserPublic
from utils.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from utils.get_collections import get_users_collection

from services.tasks import send_welcome_email

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(user: User = Body(...), users_collection=Depends(get_users_collection)):
    # Проверка на существование пользователя
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    # Хэшируем пароль
    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user.password)
    del user_dict["password"]
    result = await users_collection.insert_one(user_dict)
    send_welcome_email.delay(user.email, user.name)
    return {"id": str(result.inserted_id), "email": user.email, "name": user.name}


@router.post("/login/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], users_collection=Depends(get_users_collection)
):
    user = await authenticate_user(users_collection, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    # Генерация refresh token (например, срок жизни 7 дней)
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_access_token(
        data={"sub": user.email, "type": "refresh"}, expires_delta=refresh_token_expires
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get(
    "/profile/",
    response_model=UserPublic,
    responses={
        200: {
            "description": "User profile",
            "content": {
                "application/json": {"example": {"id": "64f09b...", "email": "user@example.com", "name": "John Doe"}}
            },
        }
    },
)
async def get_profile(current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    return UserPublic(id=current_user.id, email=current_user.email, name=current_user.name)
