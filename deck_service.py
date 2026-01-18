"""
=================================================
StudyBuddy - Deck Service
=================================================

Bu dosya:
- Deck işlemlerini service katmanında yönetir
- Auth kontrolü yapar (login zorunlu)
- Kullanıcı izolasyonunu sağlar (sadece kendi deckleri)

Not:
- Testlerle uyumlu exception tipleri kullanılır:
  - Login required  -> RuntimeError
  - Deck not found  -> ValueError
  - Permission denied -> PermissionError
"""

from auth import get_current_user
from storage import (
    create_deck,
    get_decks_by_user,
    get_deck_by_id,
    delete_deck,
)

# =================================================
# CONSTANTS (mesaj tekrarını önlemek için)
# =================================================

ERR_LOGIN_REQUIRED = "Login required"
ERR_DECK_NOT_FOUND = "Deck not found"
ERR_PERMISSION_DENIED = "Permission denied"


# ============================================
# DECK SERVICE – CREATE
# ============================================

def create_deck_for_current_user(name: str) -> dict:
    """
    Login olan kullanıcı için yeni bir deck oluşturur.

    Args:
        name: Deck adı

    Returns:
        dict: oluşturulan deck
    """
    user = get_current_user()
    if not user:
        raise RuntimeError(ERR_LOGIN_REQUIRED)

    return create_deck({
        "name": name,
        "user_id": user["id"],
    })


# ============================================
# DECK SERVICE – READ
# ============================================

def get_my_decks() -> list:
    """
    Login olan kullanıcının decklerini döndürür.

    Returns:
        list[dict]: kullanıcının deck listesi
    """
    user = get_current_user()
    if not user:
        raise RuntimeError(ERR_LOGIN_REQUIRED)

    return get_decks_by_user(user["id"])


# ============================================
# DECK SERVICE – DELETE
# ============================================

def delete_my_deck(deck_id: int) -> bool:
    """
    Login olan kullanıcı sadece kendi deckini silebilir.

    Args:
        deck_id: silinecek deck id

    Returns:
        bool: silindiyse True, silinemediyse False (storage katmanının sonucu)

    Raises:
        RuntimeError: login yoksa
        ValueError: deck bulunamazsa
        PermissionError: deck başka kullanıcıya aitse
    """
    user = get_current_user()
    if not user:
        raise RuntimeError(ERR_LOGIN_REQUIRED)

    deck = get_deck_by_id(deck_id)
    if not deck:
        raise ValueError(ERR_DECK_NOT_FOUND)

    if deck["user_id"] != user["id"]:
        raise PermissionError(ERR_PERMISSION_DENIED)

    return delete_deck(deck_id)
