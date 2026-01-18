"""
=========================================
StudyBuddy - Backup / Export Service
=========================================

Bu servis:
- Login olan kullanıcının verilerini JSON olarak export eder
- Backup dosyalarını proje kökündeki /backups klasörüne yazar
- Read-only çalışır (storage verisini değiştirmez)

Export kapsamı:
- User bilgisi
- User'a ait deck'ler
- Bu deck'lere ait card'lar
- Card'lara ait SRS state'ler
- User'a ait review kayıtları

Not:
- Backup dosyası da atomic write ile yazılır (yarım yazılma riskini azaltır).
"""


from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from auth import get_current_user
from storage import (
    atomic_write,
    load_decks,
    load_cards,
    load_srs_states,
    load_reviews,
)

# =====================================================
# CONSTANTS
# =====================================================

BACKUP_DIR = Path("backups")
ERR_NOT_LOGGED_IN = "User not logged in"

# =====================================================
# CORE BACKUP FUNCTION
# =====================================================

def export_backup_for_current_user() -> Path:
    """
    Login olan kullanıcının tüm verilerini JSON olarak export eder.

    Dönen değer:
    - Oluşturulan backup dosyasının Path'i
    """
    user = get_current_user()
    if not user:
        raise RuntimeError(ERR_NOT_LOGGED_IN)

    # backups/ klasörünü oluştur (varsa dokunmaz)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = BACKUP_DIR / f"backup_user_{user['id']}_{timestamp}.json"

    # ---------------------------------------------
    # USER'A AİT VERİLERİ TOPLA
    # ---------------------------------------------

    user_decks = [d for d in load_decks() if d["user_id"] == user["id"]]
    deck_ids = {d["id"] for d in user_decks}

    user_cards = [c for c in load_cards() if c["deck_id"] in deck_ids]
    card_ids = {c["id"] for c in user_cards}

    user_srs_states = [s for s in load_srs_states() if s["card_id"] in card_ids]
    user_reviews = [r for r in load_reviews() if r["user_id"] == user["id"]]

    # ---------------------------------------------
    # BACKUP PAYLOAD
    # ---------------------------------------------

    backup_data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
        },
        "decks": user_decks,
        "cards": user_cards,
        "srs_states": user_srs_states,
        "reviews": user_reviews,
    }

    # ---------------------------------------------
    # JSON DOSYASINA ATOMIC YAZ
    # ---------------------------------------------
    # storage.atomic_write JSON dump + fsync + os.replace yapıyor.
    atomic_write(backup_file, backup_data)

    return backup_file

# =====================================================
# CLI HELPER (MAIN İÇİN)
# =====================================================

def backup_flow() -> None:
    """
    CLI üzerinden backup alma helper'ı
    """
    try:
        path = export_backup_for_current_user()
        print("✅ Backup oluşturuldu:")
        print(path.resolve())
    except Exception as e:
        print("❌ Backup alınamadı:", e)
