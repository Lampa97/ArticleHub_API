from fastapi import status
from unittest.mock import patch


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
    user_data = {
        "email": "dupeuser@example.com",
        "name": "Dupe User",
        "password": "dupepassword"
    }
    with patch("services.tasks.send_welcome_email.delay"):
        client.post("/api/v1/auth/register/", json=user_data)
        response = client.post("/api/v1/auth/register/", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "User already exists"

def test_login_for_access_token(client):
    """
    Test user login and token retrieval.
    """
    user_data = {
        "email": "loginuser@example.com",
        "name": "Login User",
        "password": "loginpassword"
    }
    with patch("services.tasks.send_welcome_email.delay"):
        client.post("/api/v1/auth/register/", json=user_data)
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login/", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_invalid_password(client):
    """
    Test login with invalid password returns error.
    """
    user_data = {
        "email": "badpass@example.com",
        "name": "Bad Pass",
        "password": "goodpassword"
    }
    with patch("services.tasks.send_welcome_email.delay"):
        client.post("/api/v1/auth/register/", json=user_data)
    login_data = {
        "username": user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login/", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"

def test_get_profile(client):
    """
    Test retrieving user profile.
    """
    user_data = {
        "email": "profileuser@example.com",
        "name": "Profile User",
        "password": "profilepassword"
    }
    with patch("services.tasks.send_welcome_email.delay"):
        client.post("/api/v1/auth/register/", json=user_data)
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login/", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/profile/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data