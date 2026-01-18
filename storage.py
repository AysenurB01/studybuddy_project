"""
============================================
StudyBuddy - Storage Layer (JSON + Atomic I/O)
============================================

Bu dosya:
- JSON tabanlı kalıcı veri saklamayı yönetir
- Atomic write kullanır (yarım yazılma riskini önler)
- User / Deck / Card / SRS / Review CRUD işlemlerini içerir
- config.py üzerinden path yönetir (pathlib uyumlu)

ÖNEMLİ (Cascade):
- Bir deck silinince, deck'e bağlı kartlar da silinir.
- Bir kart silinince, karta bağlı SRS state ve review kayıtları da silinir.
  (Ghost data oluşmasını önler)
"""

from __future__ import annotations

from pathlib import Path
import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from config import (
    DATA_DIR,
    USERS_FILE,
    DECKS_FILE,
    CARDS_FILE,
    SRS_STATE_FILE,
    REVIEWS_FILE,
)

# =====================================================
# CORE FILE HELPERS
# =====================================================

def atomic_write(path: Path, data: Any) -> None:
    """
    Dosyayı atomik olarak yazar (yarım yazılma riskini önler).

    Yaklaşım:
    1) Aynı dizinde geçici dosyaya yaz
    2) flush + fsync (disk'e güvenli yazım)
    3) os.replace ile tek hamlede hedef dosya ile değiştir (atomic)

    Not:
    - tmp dosya aynı dizinde olduğu için aynı filesystem üzerinde kalır
      ve os.replace atomic davranır.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            delete=False,
            encoding="utf-8",
            newline="\n",
        ) as tmp:
            json.dump(data, tmp, indent=2, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)

        # Windows dahil güvenli replace (atomic)
        os.replace(str(tmp_path), str(path))

    finally:
        # Replace başarısız olursa tmp dosya kalabilir, temizle
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                # Silinemediyse önemli değil; en kötü tmp dosya kalır.
                pass


def read_json(path: Path) -> list:
    """
    JSON dosyasını okur. Dosya yoksa boş liste döndürür.
    """
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: list) -> None:
    """
    JSON dosyasını atomik şekilde yazar.
    """
    atomic_write(path, data)


def get_next_id(items: list) -> int:
    """
    Liste içindeki max id + 1 üretir.
    Liste boşsa 1 döndürür.
    """
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def initialize_storage() -> None:
    """
    data/ klasörünü ve boş JSON dosyalarını oluşturur.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for file in [USERS_FILE, DECKS_FILE, CARDS_FILE, SRS_STATE_FILE, REVIEWS_FILE]:
        if not file.exists():
            write_json(file, [])

# =====================================================
# USERS
# =====================================================

def load_users() -> List[Dict]:
    return read_json(USERS_FILE)


def save_users(users: list) -> None:
    write_json(USERS_FILE, users)


def get_user_by_email(email: str) -> Optional[Dict]:
    return next((u for u in load_users() if u["email"] == email), None)


def get_user_by_id(user_id: int) -> Optional[Dict]:
    return next((u for u in load_users() if u["id"] == user_id), None)


def create_user(data: Dict) -> Dict:
    """
    Yeni user kaydı oluşturur.

    Beklenen alanlar:
    - email, name
    - password_hash, password_salt
    """
    users = load_users()

    if get_user_by_email(data["email"]):
        raise ValueError("Email already registered")

    user = {
        "id": get_next_id(users),
        "email": data["email"],
        "password_hash": data["password_hash"],
        "password_salt": data["password_salt"],
        "name": data["name"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    users.append(user)
    save_users(users)
    return user

# =====================================================
# DECKS
# =====================================================

def load_decks() -> List[Dict]:
    return read_json(DECKS_FILE)


def save_decks(decks: list) -> None:
    write_json(DECKS_FILE, decks)


def create_deck(data: Dict) -> Dict:
    """
    Yeni deck oluşturur.
    Beklenen alanlar:
    - name
    - user_id
    """
    decks = load_decks()

    deck = {
        "id": get_next_id(decks),
        "name": data["name"],
        "user_id": data["user_id"],
    }

    decks.append(deck)
    save_decks(decks)
    return deck


def get_decks_by_user(user_id: int) -> List[Dict]:
    return [d for d in load_decks() if d["user_id"] == user_id]


def get_deck_by_id(deck_id: int) -> Optional[Dict]:
    return next((d for d in load_decks() if d["id"] == deck_id), None)


def delete_deck(deck_id: int) -> bool:
    """
    Deck siler.

    Cascade:
    - Deck'e bağlı kartlar da silinir
    - Kart silme işlemi delete_card() üzerinden yapıldığı için
      SRS state ve review kayıtları da temizlenir.
    """
    decks = load_decks()
    new_decks = [d for d in decks if d["id"] != deck_id]

    if len(decks) == len(new_decks):
        return False

    save_decks(new_decks)

    # Deck'e bağlı tüm kartları cascade ile sil
    cards = get_cards_by_deck(deck_id)
    for c in cards:
        delete_card(c["id"])

    return True

# =====================================================
# CARDS
# =====================================================

def load_cards() -> List[Dict]:
    return read_json(CARDS_FILE)


def save_cards(cards: list) -> None:
    write_json(CARDS_FILE, cards)


def get_card_by_id(card_id: int) -> Optional[Dict]:
    return next((c for c in load_cards() if c["id"] == card_id), None)


def get_cards_by_deck(deck_id: int) -> List[Dict]:
    return [c for c in load_cards() if c["deck_id"] == deck_id]


def create_card(data: Dict) -> Dict:
    """
    Yeni card oluşturur.
    Beklenen alanlar:
    - deck_id
    - front, back
    """
    cards = load_cards()

    card = {
        "id": get_next_id(cards),
        "deck_id": data["deck_id"],
        "front": data["front"],
        "back": data["back"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    cards.append(card)
    save_cards(cards)
    return card


def update_card(card_id: int, updates: Dict) -> Optional[Dict]:
    """
    Kartı günceller, güncellenen kartı döndürür.
    Bulunamazsa None döndürür.
    """
    cards = load_cards()

    for c in cards:
        if c["id"] == card_id:
            c.update(updates)
            save_cards(cards)
            return c

    return None


def delete_card(card_id: int) -> bool:
    """
    Kartı siler.

    Cascade:
    - Karta bağlı SRS state silinir
    - Karta bağlı review kayıtları silinir
    """
    cards = load_cards()
    new_cards = [c for c in cards if c["id"] != card_id]

    if len(cards) == len(new_cards):
        return False

    save_cards(new_cards)

    # Cascade temizliği
    _delete_srs_state_by_card_id(card_id)
    _delete_reviews_by_card_id(card_id)

    return True

# =====================================================
# SRS STATE
# =====================================================

def load_srs_states() -> List[Dict]:
    return read_json(SRS_STATE_FILE)


def save_srs_states(states: list) -> None:
    write_json(SRS_STATE_FILE, states)


def get_srs_state_by_card(card_id: int) -> Optional[Dict]:
    return next((s for s in load_srs_states() if s["card_id"] == card_id), None)


def create_srs_state(data: Dict) -> Dict:
    """
    Yeni SRS state oluşturur.

    Beklenen alanlar (standart):
    - user_id, card_id
    - repetition
    - interval_days
    - easiness_factor
    - due_date (ISO str)
    """
    states = load_srs_states()

    state = {
        "id": get_next_id(states),
        "user_id": data["user_id"],
        "card_id": data["card_id"],
        "repetition": data["repetition"],
        "interval_days": data["interval_days"],
        "easiness_factor": data["easiness_factor"],
        "due_date": data["due_date"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    states.append(state)
    save_srs_states(states)
    return state


def update_srs_state(state_id: int, new_data: Dict) -> None:
    """
    Mevcut SRS state'i günceller.
    Bulunamazsa ValueError fırlatır.
    """
    states = load_srs_states()

    for s in states:
        if s["id"] == state_id:
            s.update(new_data)
            s["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_srs_states(states)
            return

    raise ValueError("SRS state not found")


def _delete_srs_state_by_card_id(card_id: int) -> None:
    """
    PRIVATE: Kart silme sırasında SRS state cascade temizliği.
    """
    states = load_srs_states()
    new_states = [s for s in states if s["card_id"] != card_id]
    if len(new_states) != len(states):
        save_srs_states(new_states)

# =====================================================
# REVIEWS
# =====================================================

def load_reviews() -> List[Dict]:
    return read_json(REVIEWS_FILE)


def save_reviews(reviews: list) -> None:
    write_json(REVIEWS_FILE, reviews)


def create_review(data: Dict) -> Dict:
    """
    Yeni review kaydı oluşturur.
    Beklenen alanlar:
    - user_id, card_id
    - quality (0-5)
    - reviewed_at (ISO str)
    """
    reviews = load_reviews()

    review = {
        "id": get_next_id(reviews),
        "user_id": data["user_id"],
        "card_id": data["card_id"],
        "quality": data["quality"],
        "reviewed_at": data["reviewed_at"],
    }

    reviews.append(review)
    save_reviews(reviews)
    return review


def _delete_reviews_by_card_id(card_id: int) -> None:
    """
    PRIVATE: Kart silme sırasında review cascade temizliği.
    """
    reviews = load_reviews()
    new_reviews = [r for r in reviews if r["card_id"] != card_id]
    if len(new_reviews) != len(reviews):
        save_reviews(new_reviews)

# =====================================================
# READ-ONLY HELPERS (SERVICE LAYER)
# =====================================================

def get_all_cards() -> list:
    """Tüm kartları döndürür (read-only helper)."""
    return load_cards()


def get_all_decks() -> list:
    """Tüm deck'leri döndürür (read-only helper)."""
    return load_decks()


def get_reviews() -> list:
    """Tüm review kayıtlarını döndürür (read-only helper)."""
    return load_reviews()
