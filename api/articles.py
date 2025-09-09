from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from models.article import Article, ArticleCreate
from models.auth import UserInDB
from utils.auth import get_current_active_user
from utils.get_collections import get_articles_collection
from utils.strip import change_id_name

from services.tasks import analyze_article

router = APIRouter()


@router.post("/api/articles/", status_code=status.HTTP_201_CREATED)
async def create_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article: ArticleCreate = Body(...),
    articles_collection=Depends(get_articles_collection),
):
    article_dict = article.model_dump()

    article_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    article_dict["author"] = str(current_user.id)

    result = await articles_collection.insert_one(article_dict)

    article_dict["_id"] = str(result.inserted_id)

    change_id_name(article_dict)

    return Article(**article_dict)


@router.get("/api/articles/", status_code=status.HTTP_200_OK, response_model=list[Article])
async def list_articles(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    search: str = Query(None),
    tags: str = Query(None),
    articles_collection=Depends(get_articles_collection),
):
    query = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
        ]
    if tags:
        query["tags"] = {"$in": tags.split(",")}
    articles_cursor = articles_collection.find(query)
    articles_list = await articles_cursor.to_list(length=None)
    change_id_name(articles_list)
    return articles_list


@router.get("/api/articles/{article_id}/", status_code=status.HTTP_200_OK, response_model=Article)
async def get_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article_id: str,
    articles_collection=Depends(get_articles_collection),
):
    article_dict = await articles_collection.find_one({"_id": ObjectId(article_id)})
    if not article_dict:
        raise HTTPException(status_code=404, detail="Article not found")
    change_id_name(article_dict)
    return article_dict


@router.put("/api/articles/{article_id}/", status_code=status.HTTP_200_OK, response_model=Article)
async def update_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article_id: str,
    article: Article = Body(...),
    articles_collection=Depends(get_articles_collection),
):
    existing_article = await articles_collection.find_one({"_id": ObjectId(article_id)})
    if not existing_article:
        raise HTTPException(status_code=404, detail="Article not found")
    if existing_article["author"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this article")

    update_data = {}
    if article.title is not None:
        update_data["title"] = article.title
    if article.content is not None:
        update_data["content"] = article.content

    await articles_collection.update_one({"_id": ObjectId(article_id)}, {"$set": update_data})
    updated_article = await articles_collection.find_one({"_id": ObjectId(article_id)})
    change_id_name(updated_article)
    return updated_article


@router.delete("/api/articles/{article_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article_id: str,
    articles_collection=Depends(get_articles_collection),
):
    existing_article = await articles_collection.find_one({"_id": ObjectId(article_id)})
    if not existing_article:
        raise HTTPException(status_code=404, detail="Article not found")
    if existing_article["author"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")

    await articles_collection.delete_one({"_id": ObjectId(article_id)})
    return None


@router.post("/api/articles/{article_id}/analyze/")
async def analyze_article_endpoint(
    article_id: str,
    articles_collection=Depends(get_articles_collection)
):
    analyze_article.delay(article_id)
    return {"status": "Analysis started"}