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

router = APIRouter(prefix="/api/v1/articles", tags=["Articles"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article: ArticleCreate = Body(...),
    articles_collection=Depends(get_articles_collection),
):
    """
    Create a new article.

    This endpoint allows an authenticated user to create a new article.
    The article's author is set to the current user's ID, and the creation time is recorded.

    Args:
        current_user (UserInDB): The currently authenticated user.
        article (ArticleCreate): The article data provided in the request body.
        articles_collection: MongoDB collection for articles.

    Returns:
        Article: The newly created article with its ID and metadata.
    """
    article_dict = article.model_dump()
    article_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    article_dict["author"] = str(current_user.id)
    result = await articles_collection.insert_one(article_dict)
    article_dict["_id"] = str(result.inserted_id)
    change_id_name(article_dict)
    return Article(**article_dict)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[Article])
async def list_articles(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    search: str = Query(None),
    tags: str = Query(None),
    articles_collection=Depends(get_articles_collection),
):
    """
    List articles with optional search and tag filtering.

    This endpoint returns a list of articles. You can filter articles by search term
    (in title or content) and by tags.

    Args:
        current_user (UserInDB): The currently authenticated user.
        search (str, optional): Search term for article title or content.
        tags (str, optional): Comma-separated list of tags to filter articles.
        articles_collection: MongoDB collection for articles.

    Returns:
        list[Article]: List of articles matching the filters.
    """
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


@router.get("/{article_id}/", status_code=status.HTTP_200_OK, response_model=Article)
async def get_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article_id: str,
    articles_collection=Depends(get_articles_collection),
):
    """
    Retrieve a single article by its ID.

    Args:
        current_user (UserInDB): The currently authenticated user.
        article_id (str): The ID of the article to retrieve.
        articles_collection: MongoDB collection for articles.

    Raises:
        HTTPException: If the article is not found.

    Returns:
        Article: The requested article.
    """
    article_dict = await articles_collection.find_one({"_id": ObjectId(article_id)})
    if not article_dict:
        raise HTTPException(status_code=404, detail="Article not found")
    change_id_name(article_dict)
    return article_dict


@router.put("/{article_id}/", status_code=status.HTTP_200_OK, response_model=Article)
async def update_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article_id: str,
    article: Article = Body(...),
    articles_collection=Depends(get_articles_collection),
):
    """
    Update an existing article.

    Only the author of the article can update it. You can update the title and/or content.

    Args:
        current_user (UserInDB): The currently authenticated user.
        article_id (str): The ID of the article to update.
        article (Article): The updated article data.
        articles_collection: MongoDB collection for articles.

    Raises:
        HTTPException: If the article is not found or the user is not authorized.

    Returns:
        Article: The updated article.
    """
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


@router.delete("/{article_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    article_id: str,
    articles_collection=Depends(get_articles_collection),
):
    """
    Delete an article by its ID.

    Only the author of the article can delete it.

    Args:
        current_user (UserInDB): The currently authenticated user.
        article_id (str): The ID of the article to delete.
        articles_collection: MongoDB collection for articles.

    Raises:
        HTTPException: If the article is not found or the user is not authorized.

    Returns:
        None
    """
    existing_article = await articles_collection.find_one({"_id": ObjectId(article_id)})
    if not existing_article:
        raise HTTPException(status_code=404, detail="Article not found")
    if existing_article["author"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")

    await articles_collection.delete_one({"_id": ObjectId(article_id)})
    return None


@router.post("/{article_id}/analyze/")
async def analyze_article_endpoint(
    article_id: str,
    articles_collection=Depends(get_articles_collection)
):
    """
    Analyze an article and return the updated article with analysis results.

    This endpoint triggers an asynchronous Celery task to analyze the article (e.g., word count, unique tags).
    The response waits for the task to complete (with a timeout) and then returns the updated article,
    including the analysis results.

    Args:
        article_id (str): The ID of the article to analyze.
        articles_collection: MongoDB collection for articles.

    Raises:
        HTTPException: If the article is not found.

    Returns:
        dict: The updated article document, including the 'analysis' field.
    """
    task = analyze_article.delay(article_id)
    task.get(timeout=1)
    article_dict = await articles_collection.find_one({"_id": ObjectId(article_id)})
    if not article_dict:
        raise HTTPException(status_code=404, detail="Article not found")
    change_id_name(article_dict)
    return article_dict