"""
StudyBuddy - Yapılandırma Dosyası (config.py)

Bu dosya:
- Proje genelinde kullanılan TÜM sabitleri içerir
- Dosya / klasör yollarını merkezi olarak tanımlar
- Güvenlik, SRS ve uygulama ayarlarını barındırır

❗ NOT:
Path objeleri kullanılır, string path TANIMLANMAZ.
"""

from pathlib import Path

# =====================================================
# BASE DIRECTORY
# =====================================================

# Projenin kök dizini
BASE_DIR = Path(__file__).resolve().parent

# =====================================================
# DIRECTORY STRUCTURE
# =====================================================

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
BACKUPS_DIR = BASE_DIR / "backups"

# Gerekli klasörleri garanti altına al
for directory in (DATA_DIR, LOGS_DIR, BACKUPS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# =====================================================
# DATA FILES
# =====================================================

USERS_FILE = DATA_DIR / "users.json"
DECKS_FILE = DATA_DIR / "decks.json"
CARDS_FILE = DATA_DIR / "cards.json"

SRS_STATE_FILE = DATA_DIR / "srs_state.json"
REVIEWS_FILE = DATA_DIR / "reviews.json"
COUNTERS_FILE = DATA_DIR / "counters.json"

# =====================================================
# LOGGING
# =====================================================

LOG_FILE = LOGS_DIR / "app.log"

# =====================================================
# SM-2 ALGORITHM CONSTANTS (SRS)
# =====================================================

INITIAL_EF = 2.5        # Başlangıç easiness factor
MIN_EF = 1.3            # Minimum easiness factor
FIRST_INTERVAL = 1      # İlk tekrar (gün)
SECOND_INTERVAL = 6     # İkinci tekrar (gün)

QUALITY_DESCRIPTIONS = {
    0: "Hiç hatırlamadım",
    1: "Çok zor hatırladım",
    2: "Kısmen hatırladım",
    3: "Doğru ama zor",
    4: "Doğru ve rahat",
    5: "Mükemmel / akıcı"
}

# =====================================================
# PASSWORD SECURITY
# =====================================================

SALT_LENGTH = 32
HASH_ITERATIONS = 100_000

# =====================================================
# APPLICATION INFO
# =====================================================

APP_NAME = "StudyBuddy"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Hamit Mızrak – Öğrenci Projesi"
