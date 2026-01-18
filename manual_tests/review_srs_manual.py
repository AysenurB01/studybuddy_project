"""
Manual Test - Review & SRS Flow

Amaç:
- Review işlemi yapıldığında:
  1) Review kaydı oluşuyor mu?
  2) SRS state oluşuyor mu / güncelleniyor mu?
  3) Quality düşükse (0-2) repetition resetleniyor mu?
  4) Quality yüksekse (3-5) repetition/interval artıyor mu?

Notlar:
- Bu script CLI menülerine girmeden, servis katmanlarını direkt çağırır.
- "review_service.review_card" login gerektirir.
- Bu nedenle önce register + login yapılır.
- Email çakışmasını önlemek için her çalıştırmada benzersiz email üretir.
"""

import sys
from pathlib import Path
from datetime import date

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# =====================================================
# IMPORTS
# =====================================================

from storage import initialize_storage, get_srs_state_by_card, get_reviews
from auth import register, login, logout, get_current_user
from deck_service import create_deck_for_current_user
from card_service import create_card_for_current_user
from review_service import review_card


# =====================================================
# HELPERS
# =====================================================

def _unique_email(prefix: str = "review_srs") -> str:
    # timestamp/uuid kullanmadan da çoğu zaman yeterli benzersizlik sağlar
    return f"{prefix}_{id(prefix)}@mail.com"


def _print_state(title: str, card_id: int):
    state = get_srs_state_by_card(card_id)
    print(f"\n--- {title} ---")
    print("SRS STATE:", state)

    if state:
        print(
            f"repetition={state.get('repetition')} | "
            f"interval_days={state.get('interval_days')} | "
            f"easiness_factor={state.get('easiness_factor')} | "
            f"due_date={state.get('due_date')}"
        )


def _last_reviews_for_user(user_id: int, card_id: int, limit: int = 5):
    user_reviews = [r for r in get_reviews() if r["user_id"] == user_id and r["card_id"] == card_id]
    return user_reviews[-limit:]


def _print_last_reviews(user_id: int, card_id: int):
    items = _last_reviews_for_user(user_id, card_id)
    print("\nLast reviews (latest first):")
    for r in reversed(items):
        print(f"- quality={r['quality']} | reviewed_at={r['reviewed_at']}")


def _assert(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


# =====================================================
# RUN TEST
# =====================================================

def run_test():
    print("\n======================================")
    print(" Manual Test: Review & SRS Flow START ")
    print("======================================")

    initialize_storage()

    # -----------------------------
    # Register + Login
    # -----------------------------
    email = _unique_email("review_srs_user")
    password = "123456"
    name = "Review SRS User"

    print("\n=== REGISTER ===")
    user = register(email=email, password=password, name=name)
    print("REGISTER OK:", {"id": user["id"], "email": user["email"], "name": user["name"]})

    print("\n=== LOGIN ===")
    login(email=email, password=password)
    current = get_current_user()
    _assert(current is not None, "Login failed: current user is None")
    print("LOGIN OK:", {"id": current["id"], "email": current["email"]})

    # -----------------------------
    # Create Deck + Card
    # -----------------------------
    print("\n=== CREATE DECK ===")
    deck = create_deck_for_current_user("Review SRS Manual Deck")
    print("DECK OK:", deck)

    print("\n=== CREATE CARD ===")
    card = create_card_for_current_user(
        deck_id=deck["id"],
        front="What does SRS stand for?",
        back="Spaced Repetition System"
    )
    print("CARD OK:", card)

    card_id = card["id"]
    user_id = current["id"]

    # -----------------------------
    # Review #1 (quality=5)
    # -----------------------------
    print("\n=== REVIEW #1 (quality=5) ===")
    review_card(card_id=card_id, quality=5)
    _print_state("After Review #1", card_id)
    _print_last_reviews(user_id, card_id)

    s1 = get_srs_state_by_card(card_id)
    _assert(s1 is not None, "Expected SRS state to be created after first review")
    _assert(s1["repetition"] == 1, "Expected repetition=1 after first review")
    _assert(s1["interval_days"] >= 1, "Expected interval_days >= 1 after first review")

    # -----------------------------
    # Review #2 (quality=5)
    # -----------------------------
    print("\n=== REVIEW #2 (quality=5) ===")
    review_card(card_id=card_id, quality=5)
    _print_state("After Review #2", card_id)
    _print_last_reviews(user_id, card_id)

    s2 = get_srs_state_by_card(card_id)
    _assert(s2["repetition"] >= 2, "Expected repetition to increase on successful second review")
    _assert(s2["interval_days"] >= s1["interval_days"], "Expected interval_days to not decrease after successful review")

    # -----------------------------
    # Review #3 (quality=2) low quality -> reset
    # -----------------------------
    print("\n=== REVIEW #3 (quality=2) ===")
    review_card(card_id=card_id, quality=2)
    _print_state("After Review #3 (low quality)", card_id)
    _print_last_reviews(user_id, card_id)

    s3 = get_srs_state_by_card(card_id)
    _assert(s3["repetition"] == 1, "Expected repetition reset to 1 after low quality review (quality<3)")
    _assert(s3["interval_days"] in (1, 0), "Expected interval_days to be small (0 or 1) after low quality review")

    # due date sanity check (optional, tolerant)
    today = date.today().isoformat()
    _assert(s3["due_date"] >= today, "Expected due_date to be today or later")

    # -----------------------------
    # Logout
    # -----------------------------
    print("\n=== LOGOUT ===")
    logout()
    print("LOGOUT OK")

    print("\n====================================")
    print(" Manual Test: Review & SRS Flow PASS ")
    print("====================================")


if __name__ == "__main__":
    run_test()
