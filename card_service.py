"""
StudyBuddy - Card Service

Bu dosya:
- Card işlemlerini service katmanında yönetir
- Login & ownership kontrolü yapar
- Kullanıcı izolasyonunu garanti eder
"""

from auth import get_current_user
from storage import (
    create_card,
    get_card_by_id,
    get_cards_by_deck,
    delete_card,
    get_deck_by_id,
)
from storage import update_card


# ============================================
# CREATE CARD
# ============================================

def create_card_for_current_user(deck_id: int, front: str, back: str) -> dict:
    """
    Login olan kullanıcı için karta ekleme yapar.
    """

    user = get_current_user()
    if not user:
        raise RuntimeError("User not logged in")

    deck = get_deck_by_id(deck_id)
    if not deck:
        raise ValueError("Deck not found")

    if deck["user_id"] != user["id"]:
        raise PermissionError("You do not own this deck")

    return create_card({
        "deck_id": deck_id,
        "front": front,
        "back": back
    })


# ============================================
# LIST CARDS BY DECK (🔥 EKSİK OLAN BUYDU)
# ============================================

def get_cards_for_current_user_by_deck(deck_id: int) -> list:
    """
    Login olan kullanıcının,
    kendisine ait bir deck içindeki kartları listeler.
    """

    user = get_current_user()
    if not user:
        raise RuntimeError("User not logged in")

    deck = get_deck_by_id(deck_id)
    if not deck:
        raise ValueError("Deck not found")

    if deck["user_id"] != user["id"]:
        raise PermissionError("You do not own this deck")

    return get_cards_by_deck(deck_id)


# ============================================
# DELETE CARD
# ============================================

def delete_card_for_current_user(card_id: int) -> bool:
    """
    Login olan kullanıcı sadece kendi kartını silebilir.
    """

    user = get_current_user()
    if not user:
        raise RuntimeError("User not logged in")

    card = get_card_by_id(card_id)
    if not card:
        raise ValueError("Card not found")

    deck = get_deck_by_id(card["deck_id"])
    if not deck:
        raise ValueError("Deck not found")

    if deck["user_id"] != user["id"]:
        raise PermissionError("You do not own this card")

    return delete_card(card_id)

# =====================================================
# CARD SERVICE – READ (SINGLE CARD)
# =====================================================

def get_card_for_current_user(card_id: int) -> dict:
    """
    Login olan kullanıcının SADECE kendisine ait kartı almasını sağlar.

    Kontroller:
    - Login kontrolü
    - Card var mı?
    - Deck var mı?
    - Ownership (user_id) kontrolü
    """

    user = get_current_user()
    if not user:
        raise RuntimeError("User not logged in")

    card = get_card_by_id(card_id)
    if not card:
        raise ValueError("Card not found")

    deck = get_deck_by_id(card["deck_id"])
    if not deck:
        raise ValueError("Deck not found")

    if deck["user_id"] != user["id"]:
        raise PermissionError("You do not own this card")

    return card

# ============================
# Card Update
# ============================

def update_card_for_current_user(
    card_id: int,
    front: str | None = None,
    back: str | None = None
) -> dict:
    """
    Login olan kullanıcının SADECE kendi kartını güncellemesini sağlar.
    """

    # Login kontrolü
    user = get_current_user()
    if not user:
        raise RuntimeError("User not logged in")

    # Kart kontrolü
    card = get_card_by_id(card_id)
    if not card:
        raise ValueError("Card not found")

    # Deck kontrolü
    deck = get_deck_by_id(card["deck_id"])
    if not deck:
        raise ValueError("Deck not found")

    # Ownership
    if deck["user_id"] != user["id"]:
        raise PermissionError("You do not own this card")

    # Güncellenecek alanlar
    updates = {}
    if front is not None:
        updates["front"] = front
    if back is not None:
        updates["back"] = back

    if not updates:
        raise ValueError("Nothing to update")

    updated = update_card(card_id, updates)
    if not updated:
        raise RuntimeError("Update failed")

    return updated
