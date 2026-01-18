"""
StudyBuddy - Review Service

Bu servis:
- Login olan kullanıcının kart review yapmasını sağlar
- Review kaydı oluşturur
- SRS scheduling kurallarını uygular
"""

from datetime import datetime, timedelta, timezone

from auth import get_current_user
from card_service import get_card_for_current_user
from storage import (
    create_review,
    get_srs_state_by_card,
    create_srs_state,
    update_srs_state,
)


def review_card(card_id: int, quality: int) -> dict:
    """
    Login olan kullanıcının bir kartı review etmesini sağlar.

    Akış:
    1) Validasyon + login kontrolü
    2) Ownership kontrolü (kart kullanıcıya ait mi?)
    3) Review kaydı oluştur
    4) SRS state oluştur / güncelle
    """

    # =============================
    # Validasyon
    # =============================
    if not (0 <= quality <= 5):
        raise ValueError("Quality must be between 0 and 5")

    user = get_current_user()
    if not user:
        raise RuntimeError("User not logged in")

    # Kart + ownership kontrolü (permission hatası burada fırlayabilir)
    get_card_for_current_user(card_id)

    now = datetime.now(timezone.utc)

    # =============================
    # REVIEW KAYDI
    # =============================
    review = create_review({
        "user_id": user["id"],
        "card_id": card_id,
        "quality": quality,
        "reviewed_at": now.isoformat(),
    })

    # =============================
    # SRS STATE
    # =============================
    state = get_srs_state_by_card(card_id)

    # ---------- İlk review ----------
    if not state:
        interval_days = 1
        easiness_factor = 2.5
        repetition = 1

        create_srs_state({
            "user_id": user["id"],
            "card_id": card_id,
            "repetition": repetition,
            "interval_days": interval_days,
            "easiness_factor": easiness_factor,
            "due_date": (now + timedelta(days=interval_days)).date().isoformat(),
        })
        return review

    # ---------- EF güncelle (SM-2 benzeri) ----------
    # (Bu formül srs_service içindekiyle uyumlu)
    easiness_factor = max(
        1.3,
        state["easiness_factor"]
        + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    )

    # ---------- Low quality → reset ----------
    if quality < 3:
        repetition = 1
        interval_days = 1
    else:
        repetition = state["repetition"] + 1
        if repetition == 2:
            interval_days = 3
        else:
            # interval büyüt
            interval_days = int(state["interval_days"] * easiness_factor)
            if interval_days < 1:
                interval_days = 1

    due_date = (now + timedelta(days=interval_days)).date().isoformat()

    update_srs_state(
        state["id"],
        {
            "user_id": user["id"],
            "card_id": card_id,
            "repetition": repetition,
            "interval_days": interval_days,
            "easiness_factor": easiness_factor,
            "due_date": due_date,
        }
    )

    return review


# ==================================================
# Backward compatibility (test_review_service için)
# ==================================================
def review_card_for_current_user(card_id: int, quality: int) -> dict:
    return review_card(card_id, quality)
