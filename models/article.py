from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Article(BaseModel):
    """
    Model representing an article stored in the database.

    Attributes:
        id (str): Unique identifier of the article.
        title (str): Title of the article.
        content (str): Main content of the article.
        tags (Optional[list[str]]): List of tags associated with the article.
        author (Optional[str]): ID of the user who authored the article.
        created_at (Optional[str]): ISO-formatted creation timestamp.
    """

    id: str
    title: str
    content: str
    tags: Optional[list[str]] = []
    author: Optional[str] = None  # foreign key (user id)
    created_at: Optional[str] = None


class ArticleCreate(BaseModel):
    """
    Model for validating and documenting article creation requests.

    Attributes:
        title (str): Title of the new article.
        content (str): Content of the new article.
        tags (Optional[List[str]]): Tags for the new article.

    Example:
        {
            "title": "My Article Title",
            "content": "Article content goes here.",
            "tags": ["fastapi", "mongodb"]
        }
    """

    title: str = Field(...)
    content: str = Field(...)
    tags: Optional[List[str]] = Field(default=[])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "My Article Title",
                "content": "Article content goes here.",
                "tags": ["fastapi", "mongodb"],
            }
        }
    )
