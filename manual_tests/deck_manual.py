"""
manual_tests/deck_manual.py

StudyBuddy - Deck Service Manual Smoke Test

Amaç:
- CLI kullanmadan Deck akışını hızlıca doğrulamak
- Register/Login -> Deck oluştur -> Deck listele -> Deck sil -> Logout

Not:
- Her çalıştırmada email çakışmasın diye benzersiz email üretir.
"""

import sys
from pathlib import Path


# =====================================================
# PATH SETUP
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# =====================================================
# IMPORTS
# =====================================================

from storage import initialize_storage  # noqa: E402
from auth import register, login, logout  # noqa: E402
from deck_service import (  # noqa: E402
    create_deck_for_current_user,
    get_my_decks,
    delete_my_deck,
)


# =====================================================
# HELPERS
# =====================================================

def _unique_email(base: str = "qa") -> str:
    return f"{base}_{id(base)}@mail.com"


# =====================================================
# MANUAL RUN
# =====================================================

def main():
    initialize_storage()

    email = _unique_email("qa_deck")
    password = "123456"
    name = "QA Deck User"

    try:
        print("\n=== REGISTER + LOGIN ===")
        register(email=email, password=password, name=name)
        login(email=email, password=password)
        print("✅ Login OK:", email)

        print("\n=== CREATE DECK ===")
        deck = create_deck_for_current_user("Manual Deck")
        print("✅ Deck created:", deck)

        print("\n=== LIST MY DECKS ===")
        decks = get_my_decks()
        print("✅ My decks:", decks)

        print("\n=== DELETE DECK ===")
        deleted = delete_my_deck(deck["id"])
        print("✅ Deleted:", deleted)

        print("\n=== LIST MY DECKS (AFTER DELETE) ===")
        decks_after = get_my_decks()
        print("✅ My decks:", decks_after)

        logout()
        print("\n✅ Logout OK")

    except Exception as e:
        print("\n❌ MANUAL DECK TEST FAILED:", e)


if __name__ == "__main__":
    main()
