"""
============================================
StudyBuddy - Deck Service Tests
============================================

Bu testler:
- Deck işlemlerinin service katmanı üzerinden yapıldığını doğrular
- Auth (login / logout) zorunluluğunu test eder
- Kullanıcı izolasyonunu garanti eder
"""

import pytest

from auth import register, login, logout
from storage import get_decks_by_user

from deck_service import (
    create_deck_for_current_user,
    get_my_decks,
    delete_my_deck,
)


# ============================================
# DECK SERVICE – AUTH REQUIREMENT TESTS
# ============================================

def test_create_deck_requires_login(clean_storage):
    """
    Login olmadan deck oluşturulamaz.
    """
    with pytest.raises(Exception):
        create_deck_for_current_user("My Deck")


# ============================================
# DECK SERVICE – CREATE TESTS
# ============================================

def test_create_deck_for_logged_in_user(clean_storage, sample_user_data):
    """
    Login olan kullanıcı kendi adına deck oluşturabilmeli.
    """
    user = register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"],
    )

    login(email=sample_user_data["email"], password=sample_user_data["password"])

    deck = create_deck_for_current_user("My First Deck")

    assert deck["name"] == "My First Deck"
    assert deck["user_id"] == user["id"]


# ============================================
# DECK SERVICE – USER ISOLATION TESTS
# ============================================

def test_user_sees_only_own_decks(clean_storage, sample_user_data):
    """
    Kullanıcı sadece kendisine ait deckleri görebilmeli.
    """

    # User 1
    register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"],
    )
    login(email=sample_user_data["email"], password=sample_user_data["password"])
    create_deck_for_current_user("User1 Deck")
    logout()

    # User 2
    register(email="other@mail.com", password="123456", name="Another User")
    login(email="other@mail.com", password="123456")
    create_deck_for_current_user("User2 Deck")

    my_decks = get_my_decks()

    assert len(my_decks) == 1
    assert my_decks[0]["name"] == "User2 Deck"


# ============================================
# DECK SERVICE – DELETE TESTS
# ============================================

def test_user_can_delete_own_deck(clean_storage, sample_user_data):
    """
    Kullanıcı kendi deckini silebilmeli.
    """
    user = register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"],
    )
    login(email=sample_user_data["email"], password=sample_user_data["password"])

    deck = create_deck_for_current_user("Temporary Deck")
    deleted = delete_my_deck(deck["id"])

    assert deleted is True

    decks = get_decks_by_user(user["id"])
    assert len(decks) == 0


def test_user_cannot_delete_other_users_deck(clean_storage, sample_user_data):
    """
    Kullanıcı başka bir kullanıcıya ait decki silememeli.
    """

    # User 1 (deck sahibi)
    register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
        name=sample_user_data["name"],
    )
    login(email=sample_user_data["email"], password=sample_user_data["password"])
    deck = create_deck_for_current_user("Protected Deck")
    logout()

    # User 2 (silme denemesi)
    register(email="hack@mail.com", password="123456", name="Hacker")
    login(email="hack@mail.com", password="123456")

    with pytest.raises(Exception):
        delete_my_deck(deck["id"])
