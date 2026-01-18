"""
============================================
StudyBuddy - Review Scheduling Tests (SRS)
============================================

Bu testler, review işlemleri sonrası
Spaced Repetition System (SRS) state'inin
doğru şekilde güncellenip güncellenmediğini test eder.

Kapsam:
- İlk review'da SRS state oluşturulması
- Başarılı review'larda interval_days & repetition artışı
- Düşük quality review'larda ilerlemenin resetlenmesi
- Quality değerine göre scheduling davranışı (parametrize)

Notlar (Güncel mimari):
- User oluşturmak için storage.create_user değil auth.register kullanılır.
  (storage.create_user artık password_hash/password_salt bekler.)
- Deck oluşturmak için deck_service.create_deck_for_current_user(name: str) kullanılır.
- SRS state alan adları: repetition, interval_days, easiness_factor, due_date
"""

import pytest

from auth import register, login
from deck_service import create_deck_for_current_user
from review_service import review_card_for_current_user

from storage import (
    create_card,
    get_srs_state_by_card,
)

from utils import hash_password


# ============================================
# TEST HELPERS
# ============================================

def _unique_email(base: str = "review") -> str:
    """
    Her testte email çakışmasını önlemek için basit benzersiz email üretir.
    uuid kullanmadan da yeterli.
    """
    return f"{base}_{id(base)}@mail.com"


def _register_and_login(name: str, password: str, email_base: str) -> dict:
    """
    Kullanıcıyı register edip login yapar.
    """
    email = _unique_email(email_base)
    user = register(email=email, password=password, name=name)
    login(email=email, password=password)
    return user


# ======================================================
# TEST 1: İlk review → SRS state oluşturulmalı
# ======================================================

def test_first_review_creates_srs_state(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    İlk kez review yapılan bir kart için:
    - SRS state oluşturulmalıdır
    - interval_days = FIRST_INTERVAL (genelde 1)
    - repetition = 1
    """
    _register_and_login(
        name=sample_user_data["name"],
        password=sample_user_data["password"],
        email_base="first_review",
    )

    deck = create_deck_for_current_user(sample_deck_data["name"])

    card = create_card({
        **sample_card_data,
        "deck_id": deck["id"]
    })

    review_card_for_current_user(card_id=card["id"], quality=4)

    srs_state = get_srs_state_by_card(card["id"])

    assert srs_state is not None
    assert srs_state["card_id"] == card["id"]
    assert srs_state["repetition"] == 1
    assert srs_state["interval_days"] == 1


# ======================================================
# TEST 2: İkinci başarılı review → interval_days artmalı
# ======================================================

def test_second_review_increases_interval(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Aynı karta ikinci kez başarılı (quality >= 3) review yapıldığında:
    - repetition artmalı
    - interval_days büyümeli
    """
    _register_and_login(
        name=sample_user_data["name"],
        password=sample_user_data["password"],
        email_base="second_review",
    )

    deck = create_deck_for_current_user(sample_deck_data["name"])

    card = create_card({
        **sample_card_data,
        "deck_id": deck["id"]
    })

    # 1. Review
    review_card_for_current_user(card_id=card["id"], quality=4)
    first_state = get_srs_state_by_card(card["id"])

    # 2. Review
    review_card_for_current_user(card_id=card["id"], quality=4)
    second_state = get_srs_state_by_card(card["id"])

    assert second_state["repetition"] == first_state["repetition"] + 1
    assert second_state["interval_days"] >= first_state["interval_days"]


# ======================================================
# TEST 3: Düşük kaliteli review → ilerleme resetlenmeli
# ======================================================

def test_low_quality_review_resets_progress(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Quality < 3 olan bir review sonrası:
    - repetition resetlenmeli (1)
    - interval_days küçülmeli (genelde 1)
    """
    _register_and_login(
        name=sample_user_data["name"],
        password=sample_user_data["password"],
        email_base="low_quality",
    )

    deck = create_deck_for_current_user(sample_deck_data["name"])

    card = create_card({
        **sample_card_data,
        "deck_id": deck["id"]
    })

    # Başarılı review
    review_card_for_current_user(card_id=card["id"], quality=4)

    # Başarısız review
    review_card_for_current_user(card_id=card["id"], quality=2)

    state = get_srs_state_by_card(card["id"])

    assert state["repetition"] == 1
    assert state["interval_days"] in (1,)


# ======================================================
# TEST 4: Quality parametrize → scheduling davranışı
# ======================================================

@pytest.mark.parametrize(
    "quality, expected_repetition",
    [
        (5, 1),
        (4, 1),
        (3, 1),
        (2, 1),
        (1, 1),
        (0, 1),
    ]
)
def test_review_scheduling_by_quality(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data,
    quality,
    expected_repetition
):
    """
    Farklı quality değerleri için
    (ilk review'ta) repetition davranışı test edilir.
    İlk review'ta her durumda repetition = 1 beklenir.
    """
    _register_and_login(
        name=sample_user_data["name"],
        password=sample_user_data["password"],
        email_base=f"param_{quality}",
    )

    deck = create_deck_for_current_user(sample_deck_data["name"])

    card = create_card({
        **sample_card_data,
        "deck_id": deck["id"]
    })

    review_card_for_current_user(card_id=card["id"], quality=quality)

    state = get_srs_state_by_card(card["id"])

    assert state["repetition"] == expected_repetition
