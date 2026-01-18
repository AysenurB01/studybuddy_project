"""
============================================
StudyBuddy - Study Today Flow Tests
============================================

Bu dosya:
- "Study Today" akışının çekirdeğini (non-interactive) test eder.
- CLI içindeki input/print akışını test etmeyiz (interactive olduğu için),
  onun yerine gerçek iş kurallarını doğrularız:

Akış:
1) Kullanıcı login olur
2) Deck + Card oluşturur
3) Kart, daha önce hiç çalışılmadıysa "due" kabul edilir
4) Review sonrası SRS state oluşur ve due_date ileri taşınır
5) Aynı gün içinde kart artık due listesinde görünmez
6) Review kaydı oluşur

Not:
- register/login kullanılır (storage.create_user'a raw password verilmez).
- Testler izolasyon için clean_storage fixture'ına güvenir.
"""

from utils import hash_password
from auth import register, login
from storage import (
    create_deck,
    create_card,
    get_reviews,
)
from srs_service import (
    get_due_cards_for_current_user,
    process_review_for_card,
)


# ============================================
# TEST HELPERS
# ============================================

def _unique_email(prefix: str = "study_today") -> str:
    """
    Basit benzersiz email üretir.
    Aynı test suite içinde email çakışmalarını önler.
    """
    return f"{prefix}_{id(prefix)}@mail.com"


def _register_and_login_user(name: str, password: str) -> dict:
    """
    Register + login yapan helper.
    """
    email = _unique_email("user")
    register(email=email, password=password, name=name)
    login(email=email, password=password)
    return {"email": email, "name": name}


# ============================================
# TESTS
# ============================================

def test_due_cards_requires_login(clean_storage):
    """
    Login olmadan due kartları çekmek hata vermelidir.
    (negatif test)
    """
    try:
        get_due_cards_for_current_user()
        assert False, "Login yokken RuntimeError bekleniyordu."
    except RuntimeError:
        assert True


def test_study_today_flow_card_becomes_not_due_after_review(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Study Today çekirdek akışı:

    - Kart ilk başta due listesinde görünür (state yok)
    - Review yapılınca state oluşur
    - Aynı gün içinde kart artık due listesinde görünmez
    - Review kaydı oluşur
    """
    # ----------------------------
    # USER
    # ----------------------------
    _register_and_login_user(
        name=sample_user_data["name"],
        password=sample_user_data["password"],
    )

    # ----------------------------
    # DECK + CARD
    # ----------------------------
    # create_deck storage katmanı: user_id gerekir.

    email = _unique_email("deck_owner")
    user = register(email=email, password=sample_user_data["password"], name=sample_user_data["name"])
    login(email=email, password=sample_user_data["password"])

    deck = create_deck({
        "name": sample_deck_data["name"],
        "user_id": user["id"],
    })

    card = create_card({
        "deck_id": deck["id"],
        "front": sample_card_data["front"],
        "back": sample_card_data["back"],
    })

    # ----------------------------
    # BEFORE REVIEW: due olmalı (state yok)
    # ----------------------------
    due_before = get_due_cards_for_current_user()
    assert any(c["id"] == card["id"] for c in due_before), "Kart ilk başta due olmalıydı."

    # ----------------------------
    # REVIEW
    # ----------------------------
    reviews_before = len(get_reviews())

    state = process_review_for_card(card_id=card["id"], quality=4)
    assert state is not None
    assert state["card_id"] == card["id"]
    assert "interval_days" in state
    assert "due_date" in state

    # Review kaydı artmalı
    reviews_after = len(get_reviews())
    assert reviews_after == reviews_before + 1

    # ----------------------------
    # AFTER REVIEW: aynı gün due olmamalı
    # (FIRST_INTERVAL genelde 1 olduğu için due_date yarına gider)
    # ----------------------------
    due_after = get_due_cards_for_current_user()
    assert not any(c["id"] == card["id"] for c in due_after), "Review sonrası kart aynı gün due olmamalıydı."
