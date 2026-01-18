"""
=================================================
StudyBuddy – Storage Layer Tests
=================================================

Amaç:
- JSON tabanlı storage katmanının doğru çalıştığını doğrulamak
- CRUD işlemlerinin eksiksiz ve tutarlı olduğunu test etmek

Not:
- Bu testler auth katmanını test etmez
- Ancak auth ile UYUMLU veri üretir
"""

from storage import (
    create_user,
    get_user_by_email,

    create_deck,
    get_deck_by_id,
    delete_deck,

    create_card,
    get_card_by_id,
    update_card,
    delete_card,

    create_srs_state,
    get_srs_state_by_card,
    update_srs_state,

    create_review,
    get_reviews,
)

# =================================================
# USER TESTS
# =================================================

def test_create_user_assigns_incremental_id(clean_storage, unique_user_data):
    """
    Kullanıcı oluşturulduğunda:
    - ID otomatik atanmalı
    - İlk kullanıcı ID = 1 olmalı
    """
    user = create_user({
        "email": unique_user_data["email"],
        "name": unique_user_data["name"],
        "password_hash": unique_user_data["password_hash"],
        "password_salt": unique_user_data["password_salt"],
    })

    assert user["id"] == 1


def test_get_user_by_email_returns_correct_user(clean_storage, unique_user_data):
    """
    Email ile kullanıcı sorgulandığında
    doğru kullanıcı dönmelidir.
    """
    create_user({
        "email": unique_user_data["email"],
        "name": unique_user_data["name"],
        "password_hash": unique_user_data["password_hash"],
        "password_salt": unique_user_data["password_salt"],
    })

    user = get_user_by_email(unique_user_data["email"])
    assert user is not None
    assert user["email"] == unique_user_data["email"]


# =================================================
# DECK TESTS
# =================================================

def test_create_and_delete_deck(clean_storage, unique_user_data):
    """
    Bir deck oluşturulabilmeli ve
    silindiğinde storage’dan tamamen kalkmalıdır.
    """
    user = create_user({
        "email": unique_user_data["email"],
        "name": unique_user_data["name"],
        "password_hash": unique_user_data["password_hash"],
        "password_salt": unique_user_data["password_salt"],
    })

    deck = create_deck({
        "name": "Python Basics",
        "user_id": user["id"]
    })

    assert get_deck_by_id(deck["id"]) is not None

    delete_deck(deck["id"])
    assert get_deck_by_id(deck["id"]) is None


# =================================================
# CARD TESTS
# =================================================

def test_create_update_and_delete_card(clean_storage, unique_user_data):
    """
    Kart:
    - Oluşturulmalı
    - Güncellenmeli
    - Silinebilmelidir
    """
    user = create_user({
        "email": unique_user_data["email"],
        "name": unique_user_data["name"],
        "password_hash": unique_user_data["password_hash"],
        "password_salt": unique_user_data["password_salt"],
    })

    deck = create_deck({
        "name": "Deck",
        "user_id": user["id"]
    })

    card = create_card({
        "deck_id": deck["id"],
        "front": "Question",
        "back": "Answer"
    })

    update_card(card["id"], {"front": "Updated Question"})
    updated_card = get_card_by_id(card["id"])

    assert updated_card["front"] == "Updated Question"

    delete_card(card["id"])
    assert get_card_by_id(card["id"]) is None


# =================================================
# SRS STATE TESTS
# =================================================

def test_create_and_update_srs_state(clean_storage):
    """
    SRS state:
    - Oluşturulmalı
    - Güncellenebilmelidir
    """
    state = create_srs_state({
        "user_id": 1,
        "card_id": 1,
        "repetition": 1,
        "interval_days": 1,
        "easiness_factor": 2.5,
        "due_date": "2026-01-01"
    })

    update_srs_state(state["id"], {"interval_days": 5})

    updated_state = get_srs_state_by_card(1)
    assert updated_state["interval_days"] == 5


# =================================================
# REVIEW TESTS
# =================================================

def test_create_review(clean_storage):
    """
    Review oluşturulduğunda:
    - Storage’a kaydedilmeli
    - get_reviews() ile listelenebilmelidir
    """
    create_review({
        "user_id": 1,
        "card_id": 1,
        "quality": 4,
        "reviewed_at": "2026-01-10"
    })

    reviews = get_reviews()
    assert len(reviews) == 1
    assert reviews[0]["quality"] == 4
