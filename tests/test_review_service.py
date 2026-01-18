"""
============================================
StudyBuddy - Review Service Tests
============================================

Bu testler:
- Login olan kullanıcının kendi kartını review edebildiğini doğrular
- Başkasının kartını review etmeye çalışınca engellendiğini doğrular
- Review sonrası Review kaydı + SRS state üretildiğini kontrol eder

Önemli Not:
- utils.hash_password() dict döndürür: {"hash": "...", "salt": "..."}
"""

import pytest

from utils import hash_password
from storage import (
    create_user,
    create_deck,
    create_card,
    get_reviews,
    get_srs_state_by_card,
)

from auth import login, logout
from review_service import review_card_for_current_user


# =====================================================
# HELPERS
# =====================================================

def _create_user_with_password(email: str, name: str, password: str) -> dict:
    """
    Storage katmanına direkt user basacağımız için
    password_hash ve password_salt üretip create_user'a veriyoruz.
    """
    pwd = hash_password(password)
    return create_user({
        "email": email,
        "name": name,
        "password_hash": pwd["hash"],
        "password_salt": pwd["salt"],
    })


# =====================================================
# TESTS
# =====================================================

def test_user_can_review_own_card(clean_storage, sample_user_data, sample_deck_data, sample_card_data):
    """
    Login olan kullanıcı, kendisine ait kartı review edebilmelidir.
    Review sonrası:
    - 1 review kaydı oluşmalı
    - ilgili card için srs_state oluşmalı
    """
    # USER + LOGIN
    user = _create_user_with_password(
        email=sample_user_data["email"],
        name=sample_user_data["name"],
        password=sample_user_data["password"],
    )
    login(sample_user_data["email"], sample_user_data["password"])

    # DECK + CARD
    deck = create_deck({**sample_deck_data, "user_id": user["id"]})
    card = create_card({**sample_card_data, "deck_id": deck["id"]})

    # REVIEW
    result = review_card_for_current_user(card_id=card["id"], quality=4)

    # ASSERT: review oluştu mu?
    reviews = get_reviews()
    assert len(reviews) == 1
    assert reviews[0]["card_id"] == card["id"]
    assert reviews[0]["user_id"] == user["id"]

    # ASSERT: srs state oluştu mu?
    state = get_srs_state_by_card(card["id"])
    assert state is not None
    assert state["card_id"] == card["id"]
    assert state["user_id"] == user["id"]

    # ASSERT: fonksiyon review objesi döndürmeli
    assert result["card_id"] == card["id"]

    logout()


def test_user_cannot_review_other_users_card(clean_storage, sample_user_data, sample_deck_data, sample_card_data):
    """
    Kullanıcı, başka kullanıcıya ait kartı review edememelidir.
    """
    # USER 1 (kartın sahibi)
    user1 = _create_user_with_password(
        email=sample_user_data["email"],
        name=sample_user_data["name"],
        password=sample_user_data["password"],
    )
    login(sample_user_data["email"], sample_user_data["password"])

    deck = create_deck({**sample_deck_data, "user_id": user1["id"]})
    card = create_card({**sample_card_data, "deck_id": deck["id"]})
    logout()

    # USER 2 (başkasının kartını review etmeye çalışacak)
    _create_user_with_password(
        email="other@mail.com",
        name="Other User",
        password="654321",
    )
    login("other@mail.com", "654321")

    with pytest.raises(PermissionError):
        review_card_for_current_user(card_id=card["id"], quality=3)

    logout()
