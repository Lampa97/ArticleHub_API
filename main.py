from fastapi import FastAPI, HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from db import MongoDBConnector
from models import User, Token, UserPublic, UserInDB, Article
from typing import Annotated
from bson import ObjectId
from datetime import datetime, timezone

from datetime import timedelta
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from utils import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)



app = FastAPI()

db_connector = MongoDBConnector(app)

app.add_event_handler("startup", db_connector.startup_db_client)
app.add_event_handler("shutdown", db_connector.shutdown_db_client)

def get_users_collection():
    return app.mongodb["users"]


@app.post("/api/auth/register/", status_code=status.HTTP_201_CREATED)
async def register_user(user: User = Body(...)):
    users_collection = app.mongodb["users"]
    # Проверка на существование пользователя
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    # Хэшируем пароль
    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user.password)
    del user_dict["password"]
    result = await users_collection.insert_one(user_dict)
    return {
        "id": str(result.inserted_id),
        "email": user.email,
        "name": user.name
    }

@app.post("/api/auth/login/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await authenticate_user(app.mongodb["users"], form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    # Генерация refresh token (например, срок жизни 7 дней)
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_access_token(
        data={"sub": user.email, "type": "refresh"}, expires_delta=refresh_token_expires
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@app.get("/api/auth/profile/", response_model=UserPublic)
async def get_profile(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name
    )


@app.post("/api/articles/", status_code=status.HTTP_201_CREATED)
async def create_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article: Article = Body(...)
):
    articles_collection = app.mongodb["articles"]
    article_dict = article.model_dump()

    article_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    article_dict["author"] = str(current_user.id)
    
    result = await articles_collection.insert_one(article_dict)


    article_dict["id"] = str(result.inserted_id)

        # Если в article_dict есть другие ObjectId, тоже преобразуйте их:
    article_dict.pop("_id", None)

    
    return article_dict