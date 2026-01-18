"""
============================================
StudyBuddy - Backup Service Tests
============================================

Bu testler:
- Login olan kullanıcının verilerini JSON olarak export ettiğini doğrular
- Export dosyasının oluştuğunu ve içeriğinin beklenen şemaya uyduğunu test eder
- Testte gerçek 'backups/' klasörüne yazmamak için BACKUP_DIR monkeypatch edilir
"""

import json
from pathlib import Path
from auth import register, login, logout
from deck_service import create_deck_for_current_user
from card_service import create_card_for_current_user
from review_service import review_card

import backup_service


# ============================================
# HELPERS
# ============================================

def _unique_email(prefix: str = "backup_user") -> str:
    # Basit benzersiz email
    return f"{prefix}_{id(prefix)}@mail.com"


# ============================================
# TESTS
# ============================================

def test_export_backup_for_current_user_creates_json_file(
    clean_storage,
    sample_user_data,
    tmp_path,
    sample_deck_data,
    sample_card_data,
):
    """
    Login olan kullanıcı backup export aldığında:
    - JSON dosyası oluşturulmalı
    - Payload içinde user / decks / cards / srs_states / reviews alanları olmalı
    - Oluşturulan deck/card/review backup'a yansımalı
    """

    # -------------------------------------------------
    # 1) BACKUP_DIR'i test klasörüne yönlendir (izolasyon)
    # -------------------------------------------------
    test_backup_dir = tmp_path / "backups"
    backup_service.BACKUP_DIR = test_backup_dir

    # -------------------------------------------------
    # 2) Register + Login
    # -------------------------------------------------
    email = _unique_email("backup")
    password = sample_user_data["password"]
    name = sample_user_data["name"]

    register(email=email, password=password, name=name)
    login(email=email, password=password)

    # -------------------------------------------------
    # 3) Veri üret (deck + card + review)
    # -------------------------------------------------
    deck = create_deck_for_current_user(sample_deck_data["name"])

    card = create_card_for_current_user(
        deck_id=deck["id"],
        front=sample_card_data["front"],
        back=sample_card_data["back"],
    )

    # Review yaparak reviews + srs_state üretelim
    review_card(card_id=card["id"], quality=5)

    # -------------------------------------------------
    # 4) Export
    # -------------------------------------------------
    backup_path = backup_service.export_backup_for_current_user()

    # -------------------------------------------------
    # 5) Assert - dosya var mı?
    # -------------------------------------------------
    assert isinstance(backup_path, Path)
    assert backup_path.exists() is True
    assert backup_path.suffix == ".json"
    assert backup_path.parent == test_backup_dir

    # -------------------------------------------------
    # 6) Assert - JSON içerik kontrolü
    # -------------------------------------------------
    data = json.loads(backup_path.read_text(encoding="utf-8"))

    assert "exported_at" in data
    assert "user" in data
    assert "decks" in data
    assert "cards" in data
    assert "srs_states" in data
    assert "reviews" in data

    assert data["user"]["email"] == email
    assert data["user"]["name"] == name

    # Bu kullanıcının deck'i backup'a girmeli
    assert len(data["decks"]) == 1
    assert data["decks"][0]["id"] == deck["id"]

    # Bu deck'in card'ı backup'a girmeli
    assert len(data["cards"]) == 1
    assert data["cards"][0]["id"] == card["id"]

    # Review ve srs_state üretilmiş olmalı
    assert len(data["reviews"]) >= 1
    assert len(data["srs_states"]) >= 1

    # Temizlik
    logout()
