"""
=================================================
StudyBuddy - Pytest Fixtures (conftest.py)
=================================================

Amaç:
- Her test için izole bir storage ortamı hazırlamak
- Auth (login state) temizliğini garanti etmek
- Testlerde kullanıcı oluşturmayı standartlaştırmak (register üzerinden)

Not:
- storage.create_user artık password_hash + password_salt bekler.
- Bu yüzden testlerde doğrudan create_user yerine auth.register kullanmak en temiz çözümdür.
"""

import pytest

from auth import _reset_auth_state, register
from storage import initialize_storage
from config import DATA_DIR


# =================================================
# CORE FIXTURE: CLEAN STORAGE
# =================================================

@pytest.fixture
def clean_storage():
    """
    Her testten önce:
    - data klasöründeki json dosyalarını temizler
    - storage dosyalarını yeniden oluşturur
    - auth (login) state'ini sıfırlar
    """
    if DATA_DIR.exists():
        for file in DATA_DIR.glob("*.json"):
            file.unlink()

    initialize_storage()
    _reset_auth_state()

    yield


# =================================================
# SAMPLE DATA FIXTURES
# =================================================

@pytest.fixture
def sample_user_data():
    return {
        "email": "test@mail.com",
        "name": "Test User",
        "password": "123456",
    }


@pytest.fixture
def sample_deck_data():
    return {"name": "Test Deck"}


@pytest.fixture
def sample_card_data():
    return {"front": "Front text", "back": "Back text"}


# =================================================
# HELPER FIXTURE: REGISTERED USER CREATOR
# =================================================

@pytest.fixture
def create_registered_user():
    """
    Testlerde kullanıcı oluşturmayı standartlaştırır.
    storage.create_user yerine auth.register kullanır.

    Kullanım:
        user = create_registered_user(email="a@b.com", password="123", name="A")
    """
    def _create(email: str, password: str, name: str):
        return register(email=email, password=password, name=name)

    return _create


@pytest.fixture
def unique_user_data():
    """
    test_storage.py gibi testlerde email çakışmasını önlemek için
    her çağrıldığında benzersiz kullanıcı datası döndürür.

    Not:
    - storage.create_user password_hash / password_salt bekler
    - Bu yüzden gerçek hash/salt üretip döndürüyoruz
    """
    from utils import hash_password
    import time

    password = "123456"
    password_data = hash_password(password)

    unique_email = f"user_{time.time_ns()}@mail.com"

    return {
        "email": unique_email,
        "name": "Test User",
        "password_hash": password_data["hash"],
        "password_salt": password_data["salt"],
    }
