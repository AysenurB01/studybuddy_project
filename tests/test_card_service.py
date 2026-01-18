"""
============================================
StudyBuddy - Card Service Tests
============================================

Bu testler:
- card_service katmanının authorization (ownership) kurallarını test eder
- Login kontrolünü doğrular
- Kullanıcının sadece kendi kartlarına erişebildiğini garanti eder

Not:
- storage.create_user artık "password_hash" ve "password_salt" beklediği için
  testlerde kullanıcı oluşturmak için auth.register kullanıyoruz.
"""

import pytest

from storage import create_deck, create_card
from auth import register, login, logout
from card_service import get_card_for_current_user


# ============================================
# CARD SERVICE – AUTHORIZATION TESTS
# ============================================

def test_get_card_fails_if_user_not_logged_in(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Login olmayan kullanıcı kart alamamalıdır.
    """
    user = register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    deck = create_deck({**sample_deck_data, "user_id": user["id"]})
    card = create_card({**sample_card_data, "deck_id": deck["id"]})

    with pytest.raises(RuntimeError):
        get_card_for_current_user(card["id"])


def test_user_can_get_own_card(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Login olan kullanıcı, kendisine ait kartı alabilmelidir.
    """
    user = register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    login(email=sample_user_data["email"], password=sample_user_data["password"])

    deck = create_deck({**sample_deck_data, "user_id": user["id"]})
    card = create_card({**sample_card_data, "deck_id": deck["id"]})

    result = get_card_for_current_user(card["id"])

    assert result["id"] == card["id"]
    assert result["deck_id"] == deck["id"]


def test_user_cannot_get_other_users_card(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Kullanıcı başka bir kullanıcıya ait kartı alamamalıdır.
    """
    # ----------------------------
    # User 1 (kartın sahibi)
    # ----------------------------
    user1 = register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    login(email=sample_user_data["email"], password=sample_user_data["password"])

    deck1 = create_deck({**sample_deck_data, "user_id": user1["id"]})
    card1 = create_card({**sample_card_data, "deck_id": deck1["id"]})

    logout()

    # ----------------------------
    # User 2 (başkasının kartına erişmeye çalışır)
    # ----------------------------
    register(email="other@mail.com", password="654321", name="Other User")
    login(email="other@mail.com", password="654321")

    with pytest.raises(PermissionError):
        get_card_for_current_user(card1["id"])


def test_get_card_fails_if_card_not_found(
    clean_storage,
    sample_user_data
):
    """
    Kart yoksa ValueError fırlatılmalıdır.
    """
    register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    login(email=sample_user_data["email"], password=sample_user_data["password"])

    with pytest.raises(ValueError):
        get_card_for_current_user(999)


def test_get_card_fails_if_deck_not_found(
    clean_storage,
    sample_user_data,
    sample_card_data
):
    """
    Kartın bağlı olduğu deck yoksa hata alınmalıdır.
    """
    register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"]
    )

    login(email=sample_user_data["email"], password=sample_user_data["password"])

    # Deck olmadan kart yaratılıyor (edge case)
    card = create_card({**sample_card_data, "deck_id": 999})

    with pytest.raises(ValueError):
        get_card_for_current_user(card["id"])
