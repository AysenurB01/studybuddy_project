"""
StudyBuddy - Authentication Tests

Bu testler:
- Kullanıcı kayıt (register) işlemini doğrular
- Login / logout akışını test eder
- Aktif kullanıcı bilgisinin doğru yönetildiğini kontrol eder
"""

import pytest

from auth import register, login, logout, get_current_user


# ============================================
# AUTH – REGISTER TESTS
# ============================================

def test_register_creates_new_user(clean_storage, sample_user_data):
    """
    Yeni bir kullanıcı kayıt edildiğinde
    user objesi oluşturulmalı ve id atanmalıdır
    """

    user = register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    assert user["id"] is not None
    assert user["email"] == sample_user_data["email"]
    assert user["name"] == sample_user_data["name"]


def test_register_with_existing_email_fails(clean_storage, sample_user_data):
    """
    Aynı email ile ikinci kez kayıt yapılmaya çalışılırsa
    hata fırlatılmalıdır
    """

    register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    with pytest.raises(ValueError):
        register(
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            name=sample_user_data["name"]
        )


# ============================================
# AUTH – LOGIN / LOGOUT TESTS
# ============================================

def test_login_sets_current_user(clean_storage, sample_user_data):
    """
    Doğru bilgilerle login yapıldığında
    current user set edilmelidir
    """

    register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    logged_in = login(
        email=sample_user_data["email"],
        password=sample_user_data["password"]
    )

    assert logged_in["email"] == sample_user_data["email"]
    assert get_current_user()["email"] == sample_user_data["email"]


def test_logout_clears_current_user(clean_storage, sample_user_data):
    """
    Logout yapıldığında current user temizlenmelidir
    """

    register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    login(
        email=sample_user_data["email"],
        password=sample_user_data["password"]
    )

    logout()

    assert get_current_user() is None
