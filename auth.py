"""
StudyBuddy - Authentication Katmanı

Bu dosya:
- Register / Login / Logout işlemlerini yönetir
- Password doğrulamasını yapar
- Aktif kullanıcıyı memory'de tutar (CLI için yeterlidir)
"""

from typing import Optional, Dict
from storage import create_user, get_user_by_email
from utils import verify_password, log_info, log_error, hash_password


# =====================================================
# SESSION (CLI için basit oturum)
# =====================================================

_current_user: Optional[Dict] = None


# =====================================================
# REGISTER
# =====================================================

def register(email: str, password: str, name: str) -> Dict:
    """
    Yeni kullanıcı kaydı oluşturur.

    Kurallar:
    - Email unique
    - Password hashlenerek saklanır
    """
    log_info(f"Register attempt: {email}")

    password_data = hash_password(password)

    user = create_user({
        "email": email,
        "password_hash": password_data["hash"],
        "password_salt": password_data["salt"],
        "name": name
    })

    log_info(f"User registered: {email}")
    return user


# =====================================================
# LOGIN
# =====================================================

def login(email: str, password: str) -> Dict:
    """
    Kullanıcı giriş yapar.
    """
    global _current_user

    user = get_user_by_email(email)
    if not user:
        log_error("Login failed: user not found")
        raise ValueError("User not found")

    if not verify_password(
        password=password,
        stored_hash=user["password_hash"],
        stored_salt=user["password_salt"]
    ):
        log_error("Login failed: wrong password")
        raise ValueError("Wrong password")

    _current_user = user
    log_info(f"Login successful: {email}")
    return user


# =====================================================
# LOGOUT
# =====================================================

def logout():
    """
    Oturumu kapatır.
    """
    global _current_user

    if _current_user:
        log_info(f"Logout: {_current_user['email']}")

    _current_user = None


# =====================================================
# SESSION HELPERS
# =====================================================

def get_current_user() -> Optional[Dict]:
    """
    Aktif kullanıcıyı döndürür.
    """
    return _current_user


# =====================================================
# TEST HELPERS (pytest için)
# =====================================================

def _reset_auth_state():
    """
    SADECE TESTLER İÇİN!

    pytest sırasında:
    - Her testten önce auth state sıfırlanır
    - Testler birbirini etkilemez
    """
    global _current_user
    _current_user = None


# ============================================
# TESTING SUPPORT
# ============================================

def _set_current_user_for_testing(user: Dict):
    """
    SADECE TESTLER İÇİN!
    Normal kodda kullanılmamalı.
    """
    global _current_user
    _current_user = user