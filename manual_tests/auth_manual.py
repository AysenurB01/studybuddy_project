"""
manual_tests/auth_manual.py

StudyBuddy - Auth Manual Smoke Test

Amaç:
- CLI kullanmadan auth katmanını hızlıca elle doğrulamak
- Register / Login / Logout akışını tek dosyada smoke test etmek

Notlar:
- Bu dosya pytest testi değildir; manuel çalıştırılır.
- Aynı email ile tekrar çalıştırırsan "Email already registered" hatası alabilirsin.
  Bu yüzden aşağıda benzersiz email üretiyoruz.
"""

import sys
from pathlib import Path


# =====================================================
# PATH SETUP (proje kökünü import edilebilir yap)
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    # insert(0) -> öncelikli arama (daha güvenli)
    sys.path.insert(0, str(ROOT_DIR))


# =====================================================
# IMPORTS
# =====================================================

from storage import initialize_storage  # noqa: E402
from auth import register, login, logout  # noqa: E402


# =====================================================
# HELPERS
# =====================================================

def _unique_email(base: str = "test") -> str:
    """
    Her çalıştırmada email çakışmasını önlemek için basit benzersiz email üretir.
    """
    return f"{base}_{id(base)}@mail.com"


# =====================================================
# MANUAL RUN
# =====================================================

def main():
    initialize_storage()

    email = _unique_email("auth")
    password = "123456"
    name = "Test User"

    try:
        user = register(email, password, name)
        print("✅ REGISTER OK:", user)

        login(email, password)
        print("✅ LOGIN OK")

        logout()
        print("✅ LOGOUT OK")

    except Exception as e:
        print("❌ MANUAL AUTH TEST FAILED:", e)


if __name__ == "__main__":
    main()
