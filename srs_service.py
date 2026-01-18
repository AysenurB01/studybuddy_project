"""
StudyBuddy - SRS (Spaced Repetition) Service

Bu dosya:
- Login olan kullanıcının due kartlarını getirir
- SM-2 algoritmasının sadeleştirilmiş bir versiyonunu uygular
- Review ve SRS state kayıtlarını oluşturur
- CLI üzerinden Study Today akışını yönetir
"""

from datetime import date, timedelta

from auth import get_current_user
from storage import (
    get_cards_by_deck,
    get_decks_by_user,
    get_srs_state_by_card,
    create_srs_state,
    update_srs_state,
    create_review,
    get_user_by_id,
)

from config import INITIAL_EF, MIN_EF, FIRST_INTERVAL, SECOND_INTERVAL


# ============================================
# INTERNAL CORE (tek otorite)
# ============================================

def _process_review(user_id: int, card_id: int, quality: int) -> dict:
    """
    İç kullanım: user_id ile review işlemini yürütür.
    - Review kaydı oluşturur
    - SRS state'i oluşturur veya günceller
    - Güncel state dict döndürür

    Args:
        user_id: İşlemi yapan kullanıcı id
        card_id: Review edilen kart id
        quality: 0-5 arası kalite puanı

    Returns:
        dict: Güncel SRS state

    Raises:
        ValueError: quality aralık dışıysa
        ValueError: user bulunamazsa
    """
    if quality < 0 or quality > 5:
        raise ValueError("Quality must be between 0 and 5")

    user = get_user_by_id(user_id)
    if not user:
        raise ValueError(f"User with id {user_id} not found")

    today = date.today()
    state = get_srs_state_by_card(card_id)

    # ----------------------------
    # SRS hesaplama
    # ----------------------------
    if not state:
        # İlk kez çalışılıyorsa
        repetition = 1
        interval_days = FIRST_INTERVAL
        ef = INITIAL_EF
    else:
        # Easiness factor güncelle (SM-2 sadeleştirilmiş)
        ef = max(
            MIN_EF,
            state["easiness_factor"]
            + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )

        if quality < 3:
            # Başarısız → sıfırdan
            repetition = 1
            interval_days = FIRST_INTERVAL
        else:
            # Başarılı → aralığı büyüt
            repetition = state["repetition"] + 1
            if repetition == 2:
                interval_days = SECOND_INTERVAL
            else:
                interval_days = int(state["interval_days"] * ef)

    due_date = today + timedelta(days=interval_days)

    state_data = {
        "user_id": user_id,
        "card_id": card_id,
        "repetition": repetition,
        "interval_days": interval_days,
        "easiness_factor": ef,
        "due_date": due_date.isoformat(),
    }

    # ----------------------------
    # State yaz
    # ----------------------------
    if state:
        update_srs_state(state["id"], state_data)
    else:
        create_srs_state(state_data)

    # ----------------------------
    # Review kaydı yaz
    # ----------------------------
    create_review({
        "user_id": user_id,
        "card_id": card_id,
        "quality": quality,
        "reviewed_at": today.isoformat(),
    })

    # Güncel state'i geri döndür
    return get_srs_state_by_card(card_id)


# ============================================
# DUE CARDS
# ============================================

def get_due_cards_for_current_user() -> list:
    """
    Login olan kullanıcının bugün çalışması gereken kartları döndürür.
    HER ZAMAN card = dict döner (tuple YOK).

    Returns:
        list: Due olan kartların listesi
    """
    user = get_current_user()
    if not user:
        raise RuntimeError("Login required")

    today = date.today().isoformat()
    due_cards: list = []

    decks = get_decks_by_user(user["id"])
    for deck in decks:
        cards = get_cards_by_deck(deck["id"])
        for card in cards:
            state = get_srs_state_by_card(card["id"])

            # Daha önce hiç çalışılmamış → due
            if not state:
                due_cards.append(card)

            # Due date gelmiş → due
            elif state["due_date"] <= today:
                due_cards.append(card)

    return due_cards


# ============================================
# REVIEW PROCESSING (LOGIN USER)
# ============================================

def process_review_for_card(card_id: int, quality: int) -> dict:
    """
    Login olan kullanıcı için review işlemi yapar.

    Args:
        card_id: Kart ID'si
        quality: Kalite puanı (0-5)

    Returns:
        dict: Güncel SRS state

    Raises:
        RuntimeError: Kullanıcı login değilse
        ValueError: quality aralık dışıysa
    """
    user = get_current_user()
    if not user:
        raise RuntimeError("User not logged in")

    return _process_review(user_id=user["id"], card_id=card_id, quality=quality)


# ============================================
# BACKWARD COMPATIBILITY (TESTLER İÇİN)
# ============================================

def review_card(user_id: int, card_id: int, quality: int) -> dict:
    """
    Geriye dönük uyumluluk için bırakıldı (test_srs_service gibi eski testler).
    Login kontrolü yapmaz; direkt user_id üzerinden çalışır.

    Returns:
        dict: Güncel SRS state
    """
    return _process_review(user_id=user_id, card_id=card_id, quality=quality)


# ============================================
# STUDY TODAY – CLI
# ============================================

def study_today_for_current_user():
    """
    Login olan kullanıcının bugün çalışması gereken kartları
    CLI üzerinden çalıştırır.
    """
    user = get_current_user()
    if not user:
        raise RuntimeError("User not logged in")

    due_cards = get_due_cards_for_current_user()

    if not due_cards:
        print("🎉 Bugün çalışılacak kart yok!")
        return

    print(f"\n📚 Bugün {len(due_cards)} kart çalışacaksınız!\n")

    for i, card in enumerate(due_cards, 1):
        print(f"\n--- Kart {i}/{len(due_cards)} ---")
        print("❓ Soru:", card["front"])
        input("💡 Cevabı görmek için Enter'a basın...")

        print("✅ Cevap:", card["back"])

        while True:
            try:
                quality = int(input("\n⭐ Kalite (0-5): "))
                if 0 <= quality <= 5:
                    break
                print("❌ 0 ile 5 arasında bir sayı girin!")
            except ValueError:
                print("❌ Geçerli bir sayı girin!")

        process_review_for_card(card["id"], quality)
        print("✅ Kaydedildi!")

    print("\n🎉 Tüm kartlar tamamlandı! İyi çalışmalar!")
