from datetime import timedelta
import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.models.user import User
from app.repositories.user_repository import user_repository


@pytest.fixture(scope="module")
def auth_suffix():
    return uuid.uuid4().hex[:8]


def test_password_hashing_argon2id():
    """Verify Argon2id hashing generates valid hashes and verifies correctly."""
    raw_pwd = "SuperSecretPassword123!"
    hashed = get_password_hash(raw_pwd)
    assert hashed != raw_pwd
    assert hashed.startswith("$argon2id$")
    assert verify_password(raw_pwd, hashed)
    assert not verify_password("WrongPassword123!", hashed)


def test_create_and_decode_token():
    """Verify JWT access token creation and decoding with claims."""
    token = create_access_token(subject=42, extra_claims={"email": "test@msme.test"})
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["email"] == "test@msme.test"
    assert "exp" in payload


import jwt


def test_decode_expired_token():
    """Verify decoding an expired token raises ExpiredSignatureError."""
    token = create_access_token(
        subject=42,
        expires_delta=timedelta(seconds=-10),
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_decode_invalid_token():
    """Verify decoding a corrupt token raises PyJWTError."""
    with pytest.raises(jwt.PyJWTError):
        decode_access_token("invalid.token.payload")


def test_register_user_success(client: TestClient, db_session: Session, auth_suffix: str):
    """Test POST /api/v1/auth/register creates user and securely hashes password."""
    email = f"auth_reg_{auth_suffix}@example.com"
    payload = {
        "email": email,
        "password": "Password1234!",
        "full_name": "Priya Sharma",
        "phone_number": "+919811122233",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "Priya Sharma"
    assert data["phone_number"] == "+919811122233"
    assert data["is_active"] is True
    assert "password" not in data
    assert "hashed_password" not in data

    # Verify directly in DB
    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.hashed_password != "Password1234!"
    assert verify_password("Password1234!", user.hashed_password)


def test_register_duplicate_email(client: TestClient, auth_suffix: str):
    """Test duplicate registration returns 400 Bad Request."""
    email = f"auth_reg_{auth_suffix}@example.com"
    payload = {
        "email": email,
        "password": "DifferentPassword123!",
        "full_name": "Another Priya",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json().get("detail", "").lower()


def test_login_success_json(client: TestClient, auth_suffix: str):
    """Test POST /api/v1/auth/login with JSON body."""
    email = f"auth_reg_{auth_suffix}@example.com"
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password1234!"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


def test_login_success_form_data(client: TestClient, auth_suffix: str):
    """Test POST /api/v1/auth/login with form-urlencoded body (OAuth2/Swagger compatibility)."""
    email = f"auth_reg_{auth_suffix}@example.com"
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "Password1234!"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, auth_suffix: str):
    """Test login with wrong password returns 401."""
    email = f"auth_reg_{auth_suffix}@example.com"
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword999!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in response.json().get("detail", "").lower()


def test_login_nonexistent_email(client: TestClient):
    """Test login with nonexistent email returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent_msme_user_9999@example.com", "password": "Password123!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_inactive_user(client: TestClient, db_session: Session, auth_suffix: str):
    """Test login with inactive user account returns 400 Bad Request."""
    email = f"inactive_{auth_suffix}@example.com"
    user = User(
        email=email,
        hashed_password=get_password_hash("Password123!"),
        full_name="Inactive User",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "inactive" in response.json().get("detail", "").lower()


def test_get_me_success(client: TestClient, auth_suffix: str):
    """Test GET /api/v1/auth/me returns current user details."""
    email = f"auth_reg_{auth_suffix}@example.com"
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password1234!"},
    )
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "Priya Sharma"
    assert "password" not in data
    assert "hashed_password" not in data


def test_get_me_unauthorized_no_token(client: TestClient):
    """Test GET /api/v1/auth/me without token returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_invalid_token(client: TestClient):
    """Test GET /api/v1/auth/me with invalid token returns 401."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not_a_valid_jwt_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_expired_token(client: TestClient, db_session: Session, auth_suffix: str):
    """Test GET /api/v1/auth/me with expired token returns 401."""
    user = db_session.query(User).filter(User.email == f"auth_reg_{auth_suffix}@example.com").first()
    assert user is not None

    expired_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(seconds=-60),
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in response.json().get("detail", "").lower()


def test_user_isolation_business_profiles(client: TestClient, auth_suffix: str):
    """Test that users are strictly isolated and cannot access or modify each other's business profiles."""
    # 1. Register User A
    user_a_email = f"user_a_{auth_suffix}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": user_a_email, "password": "Password123!", "full_name": "User Alpha"},
    )
    login_a = client.post(
        "/api/v1/auth/login",
        json={"email": user_a_email, "password": "Password123!"},
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register User B
    user_b_email = f"user_b_{auth_suffix}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": user_b_email, "password": "Password123!", "full_name": "User Beta"},
    )
    login_b = client.post(
        "/api/v1/auth/login",
        json={"email": user_b_email, "password": "Password123!"},
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User A creates a business profile
    resp_create = client.post(
        "/api/v1/business-profiles",
        json={
            "business_name": "Alpha Manufacturing",
            "registration_type": "Proprietorship",
            "sector": "Manufacturing",
            "annual_turnover": 3000000.0,
        },
        headers=headers_a,
    )
    assert resp_create.status_code == status.HTTP_201_CREATED
    profile_a = resp_create.json()
    profile_a_id = profile_a["id"]

    # 4. User B attempts to access User A's profile by ID -> 403 Forbidden
    resp_b_get = client.get(
        f"/api/v1/business-profiles/{profile_a_id}",
        headers=headers_b,
    )
    assert resp_b_get.status_code == status.HTTP_403_FORBIDDEN

    # 5. User B attempts to update User A's profile -> 403 Forbidden
    resp_b_put = client.put(
        f"/api/v1/business-profiles/{profile_a_id}",
        json={"business_name": "Hacked Profile Name"},
        headers=headers_b,
    )
    assert resp_b_put.status_code == status.HTTP_403_FORBIDDEN

    # 6. User B lists their own business profiles -> should NOT see User A's profile
    resp_b_list = client.get(
        "/api/v1/business-profiles",
        headers=headers_b,
    )
    assert resp_b_list.status_code == status.HTTP_200_OK
    b_profiles = resp_b_list.json()
    assert all(p["id"] != profile_a_id for p in b_profiles)

    # 7. User A can access and update their own profile -> 200 OK
    resp_a_put = client.put(
        f"/api/v1/business-profiles/{profile_a_id}",
        json={"business_name": "Alpha Manufacturing Updated"},
        headers=headers_a,
    )
    assert resp_a_put.status_code == status.HTTP_200_OK
    assert resp_a_put.json()["business_name"] == "Alpha Manufacturing Updated"
