"""
manual_tests/card_manual.py

StudyBuddy - Card Service Manual Smoke Test

Amaç:
- CLI kullanmadan Card + Deck akışını hızlıca elle doğrulamak
- Register/Login -> Deck oluştur -> Card oluştur -> Card oku -> Logout

Notlar:
- Bu dosya pytest testi değildir; manuel çalıştırılır.
- Her çalıştırmada email çakışmasın diye benzersiz email üretir.
"""

import sys
from pathlib import Path


# =====================================================
# PATH SETUP (proje kökünü import edilebilir yap)
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# =====================================================
# IMPORTS
# =====================================================

from storage import initialize_storage  # noqa: E402
from auth import register, login, logout  # noqa: E402
from deck_service import create_deck_for_current_user  # noqa: E402
from card_service import (  # noqa: E402
    create_card_for_current_user,
    get_card_for_current_user,
)


# =====================================================
# HELPERS
# =====================================================

def _unique_email(base: str = "qa") -> str:
    """
    Her çalıştırmada email çakışmasını önlemek için basit benzersiz email üretir.
    """
    return f"{base}_{id(base)}@mail.com"


# =====================================================
# MANUAL RUN
# =====================================================

def main():
    initialize_storage()

    email = _unique_email("qa_card")
    password = "123456"
    name = "QA Card User"

    try:
        print("\n=== REGISTER + LOGIN ===")
        register(email=email, password=password, name=name)
        login(email=email, password=password)
        print("✅ Login OK:", email)

        print("\n=== CREATE DECK ===")
        deck = create_deck_for_current_user("Card Test Deck")
        print("✅ Deck created:", deck)

        print("\n=== CREATE CARD ===")
        card = create_card_for_current_user(
            deck_id=deck["id"],
            front="What is Python?",
            back="A programming language",
        )
        print("✅ Card created:", card)

        print("\n=== READ CARD ===")
        fetched = get_card_for_current_user(card["id"])
        print("✅ Card fetched:", fetched)

        logout()
        print("\n✅ Logout OK")

    except Exception as e:
        print("\n❌ MANUAL CARD TEST FAILED:", e)


if __name__ == "__main__":
    main()
