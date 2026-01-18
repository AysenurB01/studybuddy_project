"""
StudyBuddy - CLI Entry Point (Refactored)

Bu dosya:
- Uygulamayı başlatır
- CLI menülerini yönetir
- Auth / Deck / Card / SRS / Report servislerini bağlar

Amaç:
- Okunabilirlik
- Düşük cognitive complexity
- Tekrarlı literal kullanımını önleme

Çalıştırma:
    python main.py
"""

# =====================================================
# IMPORTS
# =====================================================

from storage import initialize_storage
from auth import register, login, logout, get_current_user

from deck_service import (
    create_deck_for_current_user,
    get_my_decks,
    delete_my_deck,
)

from card_service import (
    create_card_for_current_user,
    get_cards_for_current_user_by_deck,
    update_card_for_current_user,
    delete_card_for_current_user,
)

from srs_service import study_today_for_current_user

from report_service import (
    get_due_cards_for_current_user,
    get_last_7_days_activity_for_current_user,
    get_user_stats_for_current_user,
)

from backup_service import backup_flow


# =====================================================
# CONSTANTS (CLI)
# =====================================================

SELECT_PROMPT = "Select: "
BACK_OPTION = "0) Back"
ENTER_TO_CONTINUE = "\nDevam etmek için Enter..."


# =====================================================
# GENERIC HELPERS
# =====================================================

def prompt(msg: str) -> str:
    """CLI input helper"""
    return input(msg).strip()


def pause():
    """Akışı durdurmak için"""
    input(ENTER_TO_CONTINUE)


# =====================================================
# AUTH FLOWS
# =====================================================

def register_flow():
    print("\n=== Register ===")
    try:
        register(
            prompt("Email: "),
            prompt("Password: "),
            prompt("Name: "),
        )
        print("✅ Register başarılı")
    except Exception as e:
        print("❌ Hata:", e)
    pause()


def login_flow():
    print("\n=== Login ===")
    try:
        login(
            prompt("Email: "),
            prompt("Password: "),
        )
        print("✅ Login başarılı")
    except Exception as e:
        print("❌ Hata:", e)
    pause()


# =====================================================
# CARD MENU
# =====================================================

def card_menu(deck_id: int):
    """Seçilen deck içindeki kart işlemleri"""
    while True:
        print("\n--- Card Menu ---")
        print("1) Create Card")
        print("2) List Cards")
        print("3) Edit Card")
        print("4) Delete Card")
        print(BACK_OPTION)

        choice = prompt(SELECT_PROMPT)

        if choice == "1":
            create_card_for_current_user(
                deck_id,
                prompt("Front: "),
                prompt("Back: "),
            )
            print("✅ Card oluşturuldu")

        elif choice == "2":
            cards = get_cards_for_current_user_by_deck(deck_id)
            if not cards:
                print("Kart bulunamadı")
            else:
                for c in cards:
                    print(f"[{c['id']}] {c['front']}")

        elif choice == "3":
            cid = int(prompt("Card ID: "))
            update_card_for_current_user(
                cid,
                prompt("New front (boş bırak = koru): ") or None,
                prompt("New back (boş bırak = koru): ") or None,
            )
            print("✅ Card güncellendi")

        elif choice == "4":
            delete_card_for_current_user(int(prompt("Card ID: ")))
            print("✅ Card silindi")

        elif choice == "0":
            return


# =====================================================
# DECK MENU
# =====================================================

def deck_menu():
    """Deck işlemleri"""
    while True:
        print("\n--- Deck Menu ---")
        print("1) Create Deck")
        print("2) List My Decks")
        print("3) Delete Deck")
        print(BACK_OPTION)

        choice = prompt(SELECT_PROMPT)

        if choice == "1":
            deck = create_deck_for_current_user(prompt("Deck name: "))
            print(f"✅ Deck oluşturuldu (id={deck['id']})")

        elif choice == "2":
            decks = get_my_decks()
            if not decks:
                print("Deck bulunamadı")
            else:
                for d in decks:
                    print(f"[{d['id']}] {d['name']}")

                did = prompt("Card işlemleri için Deck ID gir (Enter = geç): ")
                if did.isdigit():
                    card_menu(int(did))

        elif choice == "3":
            delete_my_deck(int(prompt("Deck ID: ")))
            print("✅ Deck silindi")

        elif choice == "0":
            return


# =====================================================
# STUDY TODAY (SRS)
# =====================================================

def study_today_flow():
    print("\n--- Study Today ---")
    study_today_for_current_user()
    pause()


# =====================================================
# REPORTS MENU
# =====================================================

def reports_menu():
    while True:
        print("\n--- Reports Menu ---")
        print("1) Due Cards Today")
        print("2) Last 7 Days Activity")
        print("3) User Statistics")
        print(BACK_OPTION)

        choice = prompt(SELECT_PROMPT)

        if choice == "1":
            _show_due_cards()
        elif choice == "2":
            _show_last_7_days_activity()
        elif choice == "3":
            _show_user_stats()
        elif choice == "0":
            return


def _show_due_cards():
    print("\n--- Due Cards Today ---")
    cards = get_due_cards_for_current_user()
    if not cards:
        print("🎉 Bugün çalışılacak kart yok")
    else:
        for c in cards:
            print(f"[{c['id']}] {c['front']}")
    pause()


def _show_last_7_days_activity():
    print("\n--- Last 7 Days Activity ---")
    activity = get_last_7_days_activity_for_current_user()
    if not activity:
        print("Son 7 günde aktivite yok")
    else:
        for day, count in sorted(activity.items()):
            print(f"{day}: {count} review")
    pause()


def _show_user_stats():
    print("\n--- User Statistics ---")
    stats = get_user_stats_for_current_user()
    print(f"Total Decks     : {stats.get('total_decks', 0)}")
    print(f"Total Cards     : {stats.get('total_cards', 0)}")
    print(f"Total Reviews   : {stats.get('total_reviews', 0)}")
    print(f"Average Quality : {stats.get('average_quality', 0)}")
    pause()


# =====================================================
# MAIN MENU (AFTER LOGIN)
# =====================================================

def main_menu():
    while get_current_user():
        print("\n=== Main Menu ===")
        print("1) Decks")
        print("2) Study Today")
        print("3) Reports")
        print("4) Backup / Export")
        print("0) Logout")

        choice = prompt(SELECT_PROMPT)

        if choice == "1":
            deck_menu()
        elif choice == "2":
            study_today_flow()
        elif choice == "3":
            reports_menu()
        elif choice == "4":
            backup_flow()
            pause()
        elif choice == "0":
            logout()
            print("👋 Çıkış yapıldı")


# =====================================================
# ENTRY POINT
# =====================================================

def main():
    initialize_storage()

    while True:
        print("\n=== StudyBuddy ===")
        print("1) Register")
        print("2) Login")
        print("3) Exit")

        choice = prompt(SELECT_PROMPT)

        if choice == "1":
            register_flow()
        elif choice == "2":
            login_flow()
            if get_current_user():
                main_menu()
        elif choice == "3":
            print("👋 Görüşürüz")
            break


if __name__ == "__main__":
    main()
