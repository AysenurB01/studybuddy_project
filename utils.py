"""
StudyBuddy - Utility Fonksiyonları

Bu dosya:
- Password hashing & verification
- Logging yardımcıları içerir
"""

import os
import hashlib
import logging

from config import LOGS_DIR


# =====================================================
# LOGGING
# =====================================================

LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "studybuddy.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


def log_info(message: str):
    logging.info(message)


def log_error(message: str):
    logging.error(message)


# =====================================================
# PASSWORD HASHING
# =====================================================

def hash_password(password: str) -> dict:
    """
    Parolayı hashler.
    """
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000
    )

    return {
        "hash": hashed.hex(),
        "salt": salt.hex()
    }


def verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    """
    Girilen parolayı doğrular.
    """
    salt = bytes.fromhex(stored_salt)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000
    )
    return hashed.hex() == stored_hash

