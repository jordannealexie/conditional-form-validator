import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.security import create_access_token
from app.models.user import User, UserRole


@pytest.mark.functional
@pytest.mark.asyncio
class TestUserAuthentication:
    """test user authentication endpoints"""

    async def test_login_success(
        self, client: AsyncClient, created_user: User, test_user_data
    ):
        """test successful user login"""
        login_data = {
            "username": created_user.email,
            "password": test_user_data["password"],
        }

        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_email(self, client: AsyncClient):
        """test login fails with non-existent email"""
        login_data = {"username": "nonexistent@example.com", "password": "AnyPassword123"}

        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        
        # Depends on default exception handler
        assert "detail" in data

    async def test_login_invalid_password(
        self, client: AsyncClient, created_user: User
    ):
        """test login fails with wrong password"""
        login_data = {"username": created_user.email, "password": "WrongPassword123"}

        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()

        assert "detail" in data
