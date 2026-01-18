"""
StudyBuddy - Report Service Tests

Bu testler:
- Kullanıcıya ait due (çalışılması gereken) kartların
  doğru şekilde raporlandığını doğrular
- report_service katmanının storage ile entegrasyonunu test eder

Not:
- Report servisleri read-only olmalıdır (write yapmaz)
- Due mantığı: due_date <= today olan kartlar "due" kabul edilir
"""

from datetime import date, timedelta

from utils import hash_password

from storage import (
    create_user,
    create_deck,
    create_card,
    get_srs_state_by_card,
    update_srs_state,
)

from srs_service import review_card
from report_service import get_due_cards


# ============================================
# TEST HELPERS
# ============================================

def _unique_email(prefix: str = "report") -> str:
    """Basit benzersiz email üretir (çakışmayı engeller)."""
    return f"{prefix}_{id(prefix)}@mail.com"


def _create_user_with_password(name: str, email: str, password: str) -> dict:
    """storage.create_user hash/salt beklediği için gerçek hash/salt ile user oluşturur."""
    password_data = hash_password(password)
    return create_user({
        "email": email,
        "name": name,
        "password_hash": password_data["hash"],
        "password_salt": password_data["salt"],
    })


def _force_card_due(card_id: int, days_ago: int = 1) -> None:
    """
    Var olan SRS state'in due_date alanını geçmişe çekerek
    kartı 'due' hale getirir.
    """
    state = get_srs_state_by_card(card_id)
    assert state is not None, "SRS state should exist before forcing due_date"

    past_due_date = (date.today() - timedelta(days=days_ago)).isoformat()
    update_srs_state(state["id"], {"due_date": past_due_date})


# ============================================
# DUE CARD REPORT TESTS
# ============================================

def test_get_due_cards_returns_only_due_cards(
    clean_storage,
    sample_user_data,
    sample_deck_data,
    sample_card_data
):
    """
    Kullanıcının sadece due (çalışılması gereken) kartları raporladığını test eder.

    Akış:
    1) 2 kart oluştur
    2) İkisine de review yap → state oluşsun
    3) Sadece 1 kartı due hale getir (due_date geçmiş)
    4) Report yalnızca o kartı dönmeli
    """
    # USER
    email = _unique_email("report_user")
    user = _create_user_with_password(
        name=sample_user_data["name"],
        email=email,
        password=sample_user_data["password"],
    )

    # DECK
    deck = create_deck({**sample_deck_data, "user_id": user["id"]})

    # CARDS
    card_due = create_card({**sample_card_data, "deck_id": deck["id"], "front": "Due card"})
    card_not_due = create_card({**sample_card_data, "deck_id": deck["id"], "front": "Not due card"})

    # REVIEW → SRS STATE OLUŞTUR
    review_card(user_id=user["id"], card_id=card_due["id"], quality=2)
    review_card(user_id=user["id"], card_id=card_not_due["id"], quality=5)

    # SADECE 1 KARTI DUE YAP
    _force_card_due(card_due["id"], days_ago=1)

    # REPORT
    due_cards = get_due_cards(user["id"])

    assert len(due_cards) == 1
    assert due_cards[0]["id"] == card_due["id"]
