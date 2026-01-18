"""
StudyBuddy - Reporting Service

Bu servis:
- Kullanıcının due (çalışılması gereken) kartlarını raporlar
- Son 7 gün aktivitesini çıkarır
- Genel kullanıcı istatistiklerini üretir
- SADECE OKUMA yapar (storage write YOK)

Not:
- report_service read-only olmalı; create/update/delete çağırmaz.
"""

from datetime import date, timedelta

from auth import get_current_user
from storage import (
    get_all_cards,
    get_all_decks,
    get_reviews,
    get_srs_state_by_card,
)

# ============================================
# CONSTANTS
# ============================================

ERR_USER_NOT_LOGGED_IN = "User not logged in"


# ============================================
# INTERNAL HELPERS
# ============================================

def _get_user_deck_ids(user_id: int) -> set[int]:
    """
    Verilen kullanıcıya ait deck id setini döndürür.
    """
    return {d["id"] for d in get_all_decks() if d["user_id"] == user_id}


def _get_due_cards_for_user_id(user_id: int) -> list:
    """
    İç kullanım: Parametre olarak verilen kullanıcı için due kartları döndürür.
    """
    today = date.today().isoformat()
    due_cards: list = []

    user_deck_ids = _get_user_deck_ids(user_id)

    for card in get_all_cards():
        if card["deck_id"] not in user_deck_ids:
            continue

        state = get_srs_state_by_card(card["id"])

        if not state:
            continue

        if state["due_date"] <= today:
            due_cards.append(card)

    return due_cards


# ============================================
# DUE CARDS (PUBLIC API)
# ============================================

def get_due_cards_for_current_user() -> list:
    """
    Login olan kullanıcının due kartlarını döndürür.
    """
    user = get_current_user()
    if not user:
        raise RuntimeError(ERR_USER_NOT_LOGGED_IN)

    return _get_due_cards_for_user_id(user["id"])


def get_due_cards(user_id: int) -> list:
    """
    TEST / geriye dönük uyumluluk için:
    Kullanıcı id verilerek due kartları döndürür.

    test_report_service.py bu fonksiyonu bekliyor.
    """
    return _get_due_cards_for_user_id(user_id)


# ============================================
# LAST 7 DAYS ACTIVITY
# ============================================

def get_last_7_days_activity_for_current_user() -> dict:
    """
    Login olan kullanıcı için son 7 gün review sayılarını döndürür.
    """
    user = get_current_user()
    if not user:
        raise RuntimeError(ERR_USER_NOT_LOGGED_IN)

    today = date.today()
    start_date = today - timedelta(days=6)

    activity: dict = {}

    for r in get_reviews():
        if r["user_id"] != user["id"]:
            continue

        review_date = date.fromisoformat(r["reviewed_at"][:10])
        if start_date <= review_date <= today:
            key = review_date.isoformat()
            activity[key] = activity.get(key, 0) + 1

    return activity


# ============================================
# USER STATS
# ============================================

def get_user_stats_for_current_user() -> dict:
    """
    Login olan kullanıcı için genel istatistikler döndürür.
    """
    user = get_current_user()
    if not user:
        raise RuntimeError(ERR_USER_NOT_LOGGED_IN)

    decks = [d for d in get_all_decks() if d["user_id"] == user["id"]]
    deck_ids = {d["id"] for d in decks}

    cards = [c for c in get_all_cards() if c["deck_id"] in deck_ids]
    reviews = [r for r in get_reviews() if r["user_id"] == user["id"]]

    avg_quality = (sum(r["quality"] for r in reviews) / len(reviews)) if reviews else 0

    return {
        "total_decks": len(decks),
        "total_cards": len(cards),
        "total_reviews": len(reviews),
        "average_quality": round(avg_quality, 2),
    }
