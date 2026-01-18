"""
============================================
StudyBuddy - SRS Service Tests
============================================

Bu testler:
- SRS review akışının doğru çalıştığını doğrular
- İlk review'da state oluşturulmasını test eder
- İkinci review'da state'in güncellenmesini test eder

Not:
- Testler "gerçek" hash/salt ile user oluşturur.
- Email çakışmalarını önlemek için her testte benzersiz email kullanılır.
"""

import uuid

from utils import hash_password
from auth import login

from storage import (
    create_user,
    create_deck,
    create_card,
    get_srs_state_by_card,
    get_user_by_email,
)

from srs_service import process_review_for_card


# ============================================
# TEST HELPERS
# ============================================

def _unique_email(base: str = "test") -> str:
    """
    Her test koşusunda çakışmayacak benzersiz email üretir.
    """
    return f"{base}_{uuid.uuid4().hex}@mail.com"


def _create_user_and_login(name: str, email: str, password: str) -> dict:
    """
    Gerçek hash/salt ile user oluşturur ve login yapar.
    """
    password_data = hash_password(password)

    user = create_user({
        "email": email,
        "name": name,
        "password_hash": password_data["hash"],
        "password_salt": password_data["salt"],
    })

    # Oluşturulan user gerçekten storage'a yazılmış mı kontrol (debug için netlik)
    assert get_user_by_email(email) is not None

    login(email, password)
    return user


# ============================================
# TESTS
# ============================================

def test_first_review_creates_srs_state(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Bir kart ilk kez review edildiğinde:
    - SRS state oluşturulmalıdır
    """
    email = _unique_email("first_review")
    user = _create_user_and_login(
        name=sample_user_data["name"],
        email=email,
        password=sample_user_data["password"],
    )

    deck = create_deck({**sample_deck_data, "user_id": user["id"]})
    card = create_card({**sample_card_data, "deck_id": deck["id"]})

    # Review yap
    state = process_review_for_card(card_id=card["id"], quality=4)

    # State oluşmalı
    assert state is not None
    assert state["card_id"] == card["id"]

    # Storage'dan da bulunmalı
    stored_state = get_srs_state_by_card(card["id"])
    assert stored_state is not None
    assert stored_state["card_id"] == card["id"]


def test_second_review_updates_existing_srs_state(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Aynı kart tekrar review edildiğinde:
    - Yeni state oluşturulmamalı
    - Mevcut state güncellenmelidir
    """
    email = _unique_email("second_review")
    user = _create_user_and_login(
        name=sample_user_data["name"],
        email=email,
        password=sample_user_data["password"],
    )

    deck = create_deck({**sample_deck_data, "user_id": user["id"]})
    card = create_card({**sample_card_data, "deck_id": deck["id"]})

    first_state = process_review_for_card(card_id=card["id"], quality=4)
    second_state = process_review_for_card(card_id=card["id"], quality=5)

    assert second_state is not None
    assert second_state["card_id"] == card["id"]

    # Güncellenmiş olmalı
    assert second_state["repetition"] >= first_state["repetition"]
    assert second_state["interval_days"] >= first_state["interval_days"]
