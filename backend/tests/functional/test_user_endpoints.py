import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status

from app.core.security import create_access_token
from app.models.user import User, UserRole


async def create_auth_headers(username: str):
    """helper to create authorization headers for testing"""
    token_data = {"sub": username}
    token = create_access_token(token_data)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.functional
@pytest.mark.asyncio
class TestUserEndpointsWithAuth:
    """test user endpoints requiring authentication"""

    async def test_get_current_user_success(
        self, client: AsyncClient, created_user: User
    ):
        """test getting current user info"""
        headers = await create_auth_headers(created_user.username)

        response = await client.get("/api/v1/users/me", headers=headers)

        if response.status_code != status.HTTP_200_OK:
             print(f"DEBUG: Status {response.status_code}, Body: {response.text}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["data"]["id"] == created_user.id
        assert data["data"]["email"] == created_user.email
        assert data["data"]["first_name"] == created_user.first_name
        assert data["data"]["last_name"] == created_user.last_name

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """test getting current user without auth fails"""
        response = await client.get("/api/v1/users/me")
        
        if response.status_code != status.HTTP_401_UNAUTHORIZED:
            print(f"DEBUG: Status {response.status_code}, Body: {response.text}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """test getting current user with invalid token fails"""
        headers = {"Authorization": "Bearer invalid-token"}

        response = await client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()

        assert "detail" in data

    async def test_get_user_by_id_success(self, client: AsyncClient, created_user):
        """test getting user by id with proper auth"""
        headers = await create_auth_headers(created_user.username)

        response = await client.get(f"/api/v1/users/{created_user.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["data"]["id"] == created_user.id
        assert data["data"]["email"] == created_user.email

    async def test_get_user_by_id_not_found(self, client: AsyncClient, created_user):
        """test getting non-existent user returns null data"""
        headers = await create_auth_headers(created_user.username)

        response = await client.get("/api/v1/users/99999", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["data"] is None

    async def test_get_user_by_email_success(self, client: AsyncClient, created_user):
        """test getting user by email with proper auth"""
        headers = await create_auth_headers(created_user.username)

        response = await client.get(
            f"/api/v1/users/by-email?email={created_user.email}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["data"]["id"] == created_user.id
        assert data["data"]["email"] == created_user.email

    async def test_get_user_by_email_not_found(self, client: AsyncClient, created_user):
        """test getting user by non-existent email"""
        headers = await create_auth_headers(created_user.username)

        response = await client.get(
            "/api/v1/users/by-email?email=nonexistent@example.com", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["data"] is None


@pytest.mark.functional
class TestUserEndpointsWithRoleAuth:

    async def test_get_all_users_user_forbidden(
        self, client: AsyncClient, created_user
    ):
        headers = await create_auth_headers(created_user.username)

        response = await client.get("/api/v1/users/", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()

        assert "detail" in data
        assert "insufficient role" in data["detail"]

    async def test_get_all_users_admin_success(
        self, client: AsyncClient, created_admin, created_user
    ):
        """test admin can get all users"""
        headers = await create_auth_headers(created_admin.username)

        response = await client.get("/api/v1/users/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 2  # at least admin and user

        # find both users in response
        emails = [user["email"] for user in data["data"]]
        assert created_admin.email in emails
        assert created_user.email in emails

    async def test_get_all_users_unauthorized(self, client: AsyncClient):
        """test unauthenticated request to get all users fails"""
        response = await client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# NOTE
@pytest.mark.functional
@pytest.mark.slow
class TestFullUserFlow:
    """
    test complete user workflows end-to-end
    personally dont often do this but is an option
    """

    async def test_complete_user_registration_and_login_flow(self, client: AsyncClient):
        """test full user journey from registration to authenticated access"""
        # step 1: register new user
        registration_data = {
            "email": "fullflow@example.com",
            "username": "fullflowuser",
            "password": "FullFlowPassword123",
            "first_name": "Full",
            "last_name": "Flow",
        }

        register_response = await client.post(
            "/api/v1/auth/register", json=registration_data
        )
        assert register_response.status_code == status.HTTP_200_OK

        user_data = register_response.json()
        user_id = user_data["id"]

        # step 2: login with registered user
        login_data = {
            "username": registration_data["email"],
            "password": registration_data["password"],
        }

        login_response = await client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # step 3: access protected endpoint with token
        me_response = await client.get("/api/v1/users/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK

        me_data = me_response.json()["data"]
        assert me_data["id"] == user_id
        assert me_data["email"] == registration_data["email"]

        # step 4: access user by id
        user_response = await client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert user_response.status_code == status.HTTP_200_OK

        fetched_user = user_response.json()["data"]
        assert fetched_user["id"] == user_id
        assert fetched_user["email"] == registration_data["email"]

    async def test_admin_user_workflow(self, client: AsyncClient, created_admin):
        """test admin-specific workflows"""
        # login as admin
        login_data = {
            "username": created_admin.email,
            "password": "AdminPassword123",
        }

        login_response = await client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # access admin-only endpoint
        users_response = await client.get("/api/v1/users/", headers=headers)
        assert users_response.status_code == status.HTTP_200_OK

        users_data = users_response.json()["data"]
        assert isinstance(users_data, list)
        assert len(users_data) >= 1

        # verify admin can access own profile
        me_response = await client.get("/api/v1/users/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK

        me_data = me_response.json()["data"]
        assert me_data["role"] == UserRole.ADMIN.value
