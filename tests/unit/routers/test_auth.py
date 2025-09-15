from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status
from pydantic import ValidationError

from models.auth import User
from utils.auth import authenticate_user, get_current_user


def test_register_user(client, user_data):
    """
    Test user registration.
    """
    client.app.mongodb["users"].delete_many({})
    with patch("services.tasks.send_welcome_email.delay") as mock_delay:
        response = client.post("/api/v1/auth/register/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "id" in data
        mock_delay.assert_called_once_with(user_data["email"], user_data["name"])


def test_register_user_duplicate(client):
    """
    Test duplicate user registration returns error.
    """
    user_data = {"email": "dupeuser@example.com", "name": "Dupe_user", "password": "dupepassword1"}
    with patch("services.tasks.send_welcome_email.delay"):
        client.post("/api/v1/auth/register/", json=user_data)
        response = client.post("/api/v1/auth/register/", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "User already exists"


def test_login_for_access_token(client):
    """
    Test user login and token retrieval.
    """
    user_data = {"email": "loginuser@example.com", "name": "Login_user", "password": "loginpassword1"}
    with patch("services.tasks.send_welcome_email.delay"):
        client.post("/api/v1/auth/register/", json=user_data)
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/v1/auth/login/", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_password(client):
    """
    Test login with invalid password returns error.
    """
    user_data = {"email": "badpass@example.com", "name": "Bad_pass", "password": "goodpassword1"}
    with patch("services.tasks.send_welcome_email.delay"):
        client.post("/api/v1/auth/register/", json=user_data)
    login_data = {"username": user_data["email"], "password": "wrongpassword"}
    response = client.post("/api/v1/auth/login/", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"


def test_get_profile(client):
    """
    Test retrieving user profile.
    """
    user_data = {"email": "profileuser@example.com", "name": "Profile_user", "password": "profilepassword1"}
    with patch("services.tasks.send_welcome_email.delay"):
        client.post("/api/v1/auth/register/", json=user_data)
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/v1/auth/login/", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/profile/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data


def test_invalid_email():
    with pytest.raises(ValidationError):
        User(email="not-an-email", name="TestUser", password="Password1")


def test_name_with_spaces():
    with pytest.raises(ValidationError):
        User(email="test@example.com", name="Test User", password="Password1")


def test_short_password():
    with pytest.raises(ValidationError):
        User(email="test@example.com", name="TestUser", password="short1")


def test_password_no_digit():
    with pytest.raises(ValidationError):
        User(email="test@example.com", name="TestUser", password="Password")


def test_password_no_letter():
    with pytest.raises(ValidationError):
        User(email="test@example.com", name="TestUser", password="12345678")


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    users_collection = AsyncMock()
    users_collection.find_one.return_value = None
    result = await authenticate_user(users_collection, "notfound@example.com", "password")
    assert result is False


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    request = AsyncMock()
    request.app.mongodb = {"users": AsyncMock()}
    invalid_token = "invalid.jwt.token"
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request, invalid_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(monkeypatch):
    request = AsyncMock()
    users_collection = AsyncMock()
    users_collection.find_one.return_value = None
    request.app.mongodb = {"users": users_collection}

    from utils.auth import ALGORITHM, SECRET_KEY, create_access_token

    token = create_access_token({"sub": "notfound@example.com"})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request, token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"
