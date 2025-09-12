import pytest
from fastapi import status
from unittest.mock import patch
from bson import ObjectId

def test_create_article(client, auth_token):
    """
    Test creating a new article.
    """
    payload = {
        "title": "Test Article",
        "content": "This is a test article.",
        "tags": ["test", "fastapi"]
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/api/v1/articles/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Article"
    assert data["content"] == "This is a test article."
    assert "id" in data

def test_list_articles(client, auth_token):
    """
    Test listing articles.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/v1/articles/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_article(client, auth_token, created_article_id):
    """
    Test retrieving a single article by ID.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(f"/api/v1/articles/{created_article_id}/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_article_id

def test_update_article(client, auth_token, created_article_id):
    """
    Test updating an existing article.
    """
    payload = {
        "id": created_article_id,  # если требуется
        "title": "Updated Title",
        "content": "Updated content.",
        "tags": ["updated"],
        "author": "testuser@example.com",  # или id пользователя, если требуется
        "created_at": "2025-09-11T08:25:33.170069+00:00"  # если требуется
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put(f"/api/v1/articles/{created_article_id}/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content."

def test_delete_article(client, auth_token, created_article_id):
    """
    Test deleting an article.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.delete(f"/api/v1/articles/{created_article_id}/", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_analyze_article_mocked(client, auth_token, created_article_id):
    """
    Test analyzing an article (Celery task is mocked, analysis field is set manually).
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    with patch("services.tasks.analyze_article.delay") as mock_delay:
        mock_delay.return_value.get.return_value = None
        client.app.mongodb.articles.update_one(
            {"_id": ObjectId(created_article_id)},
            {"$set": {"analysis": {"word_count": 5, "unique_tags": 2}}}
        )
        response = client.post(f"/api/v1/articles/{created_article_id}/analyze/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "analysis" in data
        mock_delay.assert_called_once_with(created_article_id)