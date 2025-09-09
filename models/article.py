from pydantic import BaseModel, Field
from typing import Optional, List


class Article(BaseModel):
    id: str
    title: str
    content: str
    tags: Optional[list[str]] = []
    author: Optional[str] = None  # foreign key (id пользователя)
    created_at: Optional[str] = None

class ArticleCreate(BaseModel):
    title: str = Field(..., example="My Article Title")
    content: str = Field(..., example="Article content goes here.")
    tags: Optional[List[str]] = Field(default=[], example=["fastapi", "mongodb"])

    class Config:
        schema_extra = {
            "example": {
                "title": "My Article Title",
                "content": "Article content goes here.",
                "tags": ["fastapi", "mongodb"]
            }
        }