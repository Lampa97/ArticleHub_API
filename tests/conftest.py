import pytest
from fastapi.testclient import TestClient

from tests.setup import app


@pytest.fixture(scope="session")
def client():
    """
    Provides a FastAPI TestClient instance for testing.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_token(client):
    """
    Registers and logs in a test user, returning a valid JWT token.
    """
    user_data = {"email": "testuser@example.com", "name": "Test User", "password": "testpassword"}
    client.post("/api/v1/auth/register/", json=user_data)
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/v1/auth/login/", data=login_data)
    token = response.json()["access_token"]
    return token


@pytest.fixture
def user_data():
    """
    Returns default user data for registration and login tests.
    """
    return {"email": "testuser@example.com", "name": "Test User", "password": "testpassword"}


@pytest.fixture
def registered_user(client, user_data):
    """
    Registers a user and returns the user data.
    """
    client.post("/api/v1/auth/register/", json=user_data)
    return user_data


@pytest.fixture
def created_article_id(client, auth_token):
    """
    Creates a test article and returns its ID.
    """
    payload = {"title": "Test Article", "content": "This is a test article.", "tags": ["test", "fastapi"]}
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/api/v1/articles/", json=payload, headers=headers)
    return response.json()["id"]
