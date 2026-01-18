"""
======================================
Manual Test - Backup / Export
======================================

Bu script:
- Storage'ı initialize eder
- Register + Login yapar
- Deck + Card oluşturur
- 1 review yaparak SRS state üretir
- Backup export alır ve dosya yolunu yazdırır

Çalıştırma:
    python manual_tests/backup_manual.py
"""

import sys
from pathlib import Path
import time
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from storage import initialize_storage
from auth import register, login, logout
from deck_service import create_deck_for_current_user
from card_service import create_card_for_current_user
from review_service import review_card
from backup_service import export_backup_for_current_user


def _unique_email(prefix: str = "backup_manual") -> str:
    return f"{prefix}_{int(time.time() * 1000)}@mail.com"


def run_test():
    print("\n======================================")
    print(" Manual Test: Backup / Export START ")
    print("======================================\n")

    initialize_storage()

    email = _unique_email()
    password = "123456"
    name = "Backup Manual User"

    print("=== REGISTER ===")
    user = register(email=email, password=password, name=name)
    print("REGISTER OK:", user)

    print("\n=== LOGIN ===")
    login_user = login(email=email, password=password)
    print("LOGIN OK:", login_user)

    print("\n=== CREATE DECK ===")
    deck = create_deck_for_current_user("Backup Manual Deck")
    print("DECK OK:", deck)

    print("\n=== CREATE CARD ===")
    card = create_card_for_current_user(
        deck_id=deck["id"],
        front="What is backup?",
        back="Exporting data as a JSON snapshot",
    )
    print("CARD OK:", card)

    print("\n=== REVIEW (quality=5) ===")
    review = review_card(card_id=card["id"], quality=5)
    print("REVIEW OK:", review)

    print("\n=== EXPORT BACKUP ===")
    backup_path = export_backup_for_current_user()
    print("BACKUP FILE:", backup_path.resolve())

    # JSON preview (kısa kontrol)
    try:
        data = json.loads(Path(backup_path).read_text(encoding="utf-8"))
        print("\nBackup keys:", list(data.keys()))
        print("Decks:", len(data.get("decks", [])))
        print("Cards:", len(data.get("cards", [])))
        print("Reviews:", len(data.get("reviews", [])))
        print("SRS States:", len(data.get("srs_states", [])))
    except Exception as e:
        print("⚠️ JSON preview failed:", e)

    print("\n=== LOGOUT ===")
    logout()
    print("LOGOUT OK")

    print("\n====================================")
    print(" Manual Test: Backup / Export PASS ")
    print("====================================\n")


if __name__ == "__main__":
    run_test()
