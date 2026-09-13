import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.business_profile import BusinessProfile
from app.core.security import verify_password


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


def test_create_user(client: TestClient, db_session: Session, unique_suffix: str):
    """Test user creation with Argon2 password hashing."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    user_payload = {
        "email": email,
        "full_name": "Ramesh Kumar Sharma",
        "phone_number": "+919876543210",
        "password": "SecurePassword123!",
        "is_active": True,
        "is_superuser": False,
    }
    response = client.post("/api/v1/users", json=user_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["email"] == email
    assert data["full_name"] == "Ramesh Kumar Sharma"
    assert "password" not in data
    assert "hashed_password" not in data

    # Verify directly in DB that password was hashed with Argon2
    user_in_db = db_session.query(User).filter(User.email == email).first()
    assert user_in_db is not None
    assert user_in_db.hashed_password != "SecurePassword123!"
    assert verify_password("SecurePassword123!", user_in_db.hashed_password)


def test_create_user_duplicate_email(client: TestClient, unique_suffix: str):
    """Test that registering an already registered email returns 400 Bad Request."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    user_payload = {
        "email": email,
        "full_name": "Duplicate User",
        "password": "AnotherPassword456!",
    }
    response = client.post("/api/v1/users", json=user_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "already registered" in data.get("detail", "").lower()


def test_get_user_by_id(client: TestClient, db_session: Session, unique_suffix: str):
    """Test retrieving user details by ID."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    target_user = db_session.query(User).filter(User.email == email).first()
    assert target_user is not None
    target_id = target_user.id

    response = client.get(f"/api/v1/users/{target_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == target_id


def test_get_nonexistent_user(client: TestClient):
    """Test that retrieving nonexistent user returns 404."""
    response = client.get("/api/v1/users/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user(client: TestClient, db_session: Session, unique_suffix: str):
    """Test updating user attributes."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    target_user = db_session.query(User).filter(User.email == email).first()
    assert target_user is not None
    target_id = target_user.id

    update_payload = {
        "full_name": "Ramesh K. Sharma (Updated)",
        "phone_number": "+919876543299",
    }
    response = client.put(f"/api/v1/users/{target_id}", json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Ramesh K. Sharma (Updated)"
    assert data["phone_number"] == "+919876543299"


def _get_auth_headers(client: TestClient, email: str, password: str = "SecurePassword123!") -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        client.post("/api/v1/users", json={
            "email": email,
            "password": password,
            "full_name": "Test User",
        })
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_business_profile_for_user(client: TestClient, db_session: Session, unique_suffix: str):
    """Test creating a business profile associated with a user."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    target_user = db_session.query(User).filter(User.email == email).first()
    assert target_user is not None
    user_id = target_user.id
    headers = _get_auth_headers(client, email)

    udyam_no = f"UDYAM-RJ-{unique_suffix[:4].upper()}-00123"
    profile_payload = {
        "business_name": "Sharma Precision Tools",
        "registration_type": "Proprietorship",
        "udyam_registration_number": udyam_no,
        "enterprise_type": "Micro",
        "sector": "Manufacturing",
        "nic_code": "25920",
        "state": "Rajasthan",
        "district": "Jaipur",
        "is_rural": False,
        "annual_turnover": 4500000.0,
        "investment_in_plant": 1200000.0,
        "employee_count": 8,
    }
    response = client.post(
        f"/api/v1/users/{user_id}/business-profiles",
        json=profile_payload,
        headers=headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["business_name"] == "Sharma Precision Tools"
    assert data["user_id"] == user_id
    assert data["udyam_registration_number"] == udyam_no
    assert data["annual_turnover"] == 4500000.0


def test_create_business_profile_duplicate_udyam(client: TestClient, db_session: Session, unique_suffix: str):
    """Test that creating a profile with duplicate UDYAM registration fails."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    target_user = db_session.query(User).filter(User.email == email).first()
    assert target_user is not None
    user_id = target_user.id
    headers = _get_auth_headers(client, email)

    udyam_no = f"UDYAM-RJ-{unique_suffix[:4].upper()}-00123"
    duplicate_payload = {
        "business_name": "Duplicate Tools",
        "udyam_registration_number": udyam_no,
        "sector": "Manufacturing",
    }
    response = client.post(
        f"/api/v1/users/{user_id}/business-profiles",
        json=duplicate_payload,
        headers=headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json().get("detail", "").lower()


def test_list_business_profiles_for_user(client: TestClient, db_session: Session, unique_suffix: str):
    """Test listing all business profiles for a specific user."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    target_user = db_session.query(User).filter(User.email == email).first()
    assert target_user is not None
    user_id = target_user.id
    headers = _get_auth_headers(client, email)

    response = client.get(f"/api/v1/users/{user_id}/business-profiles", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    profiles = response.json()
    assert isinstance(profiles, list)
    assert len(profiles) >= 1
    assert profiles[0]["user_id"] == user_id


def test_get_business_profile_by_id(client: TestClient, unique_suffix: str):
    """Test retrieving a single business profile by ID."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    headers = _get_auth_headers(client, email)

    all_resp = client.get("/api/v1/business-profiles", headers=headers)
    assert all_resp.status_code == status.HTTP_200_OK
    profiles = all_resp.json()
    assert len(profiles) > 0
    profile_id = profiles[0]["id"]

    response = client.get(f"/api/v1/business-profiles/{profile_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == profile_id


def test_get_nonexistent_business_profile(client: TestClient, unique_suffix: str):
    """Test retrieving nonexistent business profile returns 404."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    headers = _get_auth_headers(client, email)
    response = client.get("/api/v1/business-profiles/999999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_business_profile(client: TestClient, unique_suffix: str):
    """Test updating business profile fields."""
    email = f"entrepreneur_{unique_suffix}@msme.test"
    headers = _get_auth_headers(client, email)

    all_resp = client.get("/api/v1/business-profiles", headers=headers)
    profile_id = all_resp.json()[0]["id"]

    update_payload = {
        "annual_turnover": 5200000.0,
        "employee_count": 10,
    }
    response = client.put(f"/api/v1/business-profiles/{profile_id}", json=update_payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["annual_turnover"] == 5200000.0
    assert data["employee_count"] == 10
