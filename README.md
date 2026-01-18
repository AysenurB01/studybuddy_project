# 📚 StudyBuddy

[![Python Version](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![Testing: pytest](https://img.shields.io/badge/testing-pytest-green.svg)](https://pytest.org/)
[![Code Style: Clean Architecture](https://img.shields.io/badge/architecture-layered-purple.svg)]()

> A pure Python CLI-based flashcard application implementing the Spaced Repetition System (SRS) for efficient learning.

---

## 📖 Overview

**StudyBuddy** is a command-line flashcard study application that leverages the proven **Spaced Repetition System (SM-2 algorithm)** to optimize long-term memory retention. Built entirely with Python's standard library, it provides a robust, file-based persistence layer without external database dependencies. The project was developed using a **Test-Driven Development (TDD)** approach, with business logic validated through automated and manual tests.

### Purpose

- Enable efficient flashcard-based studying with scientifically-backed SRS scheduling
- Track learning progress through reports and statistics
- Provide secure, isolated study environments for multiple users
- Demonstrate clean architecture and professional software engineering practices

---

## ✨ Key Features

### 🔐 User Management
- Secure registration with hashed passwords (PBKDF2 + salt)
- Session-based authentication
- Complete user data isolation

### 📦 Deck Management
- Create, list, and delete study decks
- Cascade deletion (removes associated cards automatically)
- Per-user deck organization

### 🃏 Card Management
- Add flashcards with front (question) and back (answer)
- Full CRUD operations
- Automatic SRS state initialization

### 🎯 Smart Review System
- Quality-based scoring (0-5 scale)
- SM-2 algorithm implementation for interval calculation
- Automatic due date scheduling
- Progress tracking per card

### 📊 Analytics & Reporting
- Today's due cards
- Last 7 days review statistics
- User-level study statistics

### 💾 Backup & Export
- Timestamped JSON exports
- Full user data backup
- Easy data migration

---

## 🛠️ Technical Stack

| Component    | Technology                  |
|--------------|-----------------------------|
| Language     | Python 3.14                 |
| Interface    | CLI (Command Line)          |
| Storage      | JSON (file-based)           |
| Testing      | pytest                      |
| Dependencies | Standard Library Only*      |
| Architecture | Layered (Service + Storage) |

_*pytest required for testing only, not for runtime_

---

## 📋 Requirements
> Manual tests are executed directly via the CLI and do not require any additional tools.

### System Requirements
- Python 3.14 (developed and tested)
- No external runtime dependencies

### Development Requirements
```bash
pytest  # Required only for running automated tests
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AysenurB01/studybuddy.git
cd studybuddy
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Activate on Linux/Mac
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

### 3. Install Test Dependencies (Optional)
```bash
pip install pytest
```
> Required only for running automated tests. Not needed for normal CLI usage.

### 4. Run the Application
```bash
python main.py
```
>This command starts the interactive CLI menu.
---

## 🏗️ Project Architecture

### Layered (Clean) Architecture Design

```
┌─────────────────────────────────────┐
│         CLI Interface (main.py)     │
├─────────────────────────────────────┤
│       Service Layer                 │
│  ┌──────────────────────────────┐   │
│  │ auth | deck | card | review  │   │
│  │ report | srs | backup        │   │
│  └──────────────────────────────┘   │
├─────────────────────────────────────┤
│    Storage Layer (storage.py)       │
│    - Atomic writes                  │
│    - JSON persistence               │
│    - ID generation                  │
└─────────────────────────────────────┘
```

This layered design ensures:
- Clear separation of concerns
- Testable business logic independent from CLI
- Safe file-based persistence with atomic writes
- Easier maintenance and future extensibility

### Core Modules

| Module              | Responsibility                              |
|---------------------|---------------------------------------------|
| `main.py`           | CLI menu and application entry point        |
| `storage.py`        | JSON I/O, atomic writes, ID generation      |
| `auth.py`           | Registration, login, password hashing       |
| `deck_service.py`   | Deck business logic                         |
| `card_service.py`   | Card CRUD operations                        |
| `review_service.py` | Review validation and persistence           |
| `srs_service.py`    | SRS scheduling and SM-2 algorithm           |
| `report_service.py` | Analytics and statistics                    |
| `backup_service.py` | Data export functionality                   |
| `config.py`         | Centralized configuration and constants     |
| `utils.py`          | Logging, password hashing, shared utilities |

---

## 📁 Folder Structure

```
studybuddy_project/
│
├── backups/                 # JSON backup exports
│
├── data/                    # JSON data storage
│   ├── users.json
│   ├── decks.json
│   ├── cards.json
│   ├── srs_state.json
│   └── reviews.json
│
├── logs/
│   └── studybuddy.log
│
├── manual_tests/             # Manual QA assets (5 scripts + 4 docs)
│   ├── auth_manual.py
│   ├── deck_manual.py
│   ├── card_manual.py
│   ├── review_srs_manual.py
│   ├── backup_manual.py
│   ├── test_plan_manual.md
│   ├── test_scenarios_manual.md
│   ├── test_cases_manual.md
│   └── test_report_manual.md
│
├── tests/                    # Automated pytest tests (37 tests)
│   ├── __init__.py           # optional
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_storage.py
│   ├── test_deck_service.py
│   ├── test_card_service.py
│   ├── test_review_service.py
│   ├── test_review_scheduling.py
│   ├── test_srs_service.py
│   ├── test_report_service.py
│   ├── test_backup_service.py
│   └── test_study_today_flow.py
│
├── auth.py
├── backup_service.py
├── card_service.py
├── config.py
├── deck_service.py
├── main.py
├── report_service.py
├── review_service.py
├── srs_service.py
├── storage.py
├── utils.py
├── README.md
└── .gitignore
```

---

## 📊 Data Model (JSON)

StudyBuddy uses file-based JSON storage under `data/`.

- **users.json**:  
  `id`, `email`, `name`, `password_hash`, `password_salt`, `created_at`

- **decks.json**:  
  `id`, `user_id`, `name`

- **cards.json**:  
  `id`, `deck_id`, `front`, `back`, `created_at`

- **srs_state.json**:  
  `id`, `user_id`, `card_id`, `repetition`, `interval_days`,  
  `easiness_factor`, `due_date`, `created_at`, `updated_at?`

- **reviews.json**:  
  `id`, `user_id`, `card_id`, `quality`, `reviewed_at`

**Notes**
- `due_date` is stored as an ISO date string (`YYYY-MM-DD`)
- Writes are atomic to reduce JSON corruption risk
- Cascade delete prevents orphan records  
  (`deck → cards`, `card → srs_state + reviews`)

---

## 💻 Usage

### Main Menu

```
====== STUDYBUDDY ======
1. Register
2. Login
3. Exit

------ Main Menu ------  #(After Login)
1. Deck 
2. Study Today
3. Reports
4. Backup / Export
0. Logout

------ Card Menu ------
1) Create Card
2) List Cards
3) Edit Card
4) Delete Card
0) Back
```

---

## 🔬 Technical Notes

### Spaced Repetition (SM-2, simplified)
- Reviews are scored with a **quality** value from **0 to 5**.
- The scheduler updates:
  - `easiness_factor` (min bounded)
  - `repetition`
  - `interval_days`
  - `due_date` (ISO date: `YYYY-MM-DD`)
- Low-quality reviews (**quality < 3**) reset progress (repetition/interval).

### Security
- Passwords are stored using **PBKDF2-HMAC-SHA256 + per-user salt**.
- Authentication is session-based (in-memory current user).

### Data Integrity
- **Atomic writes** are used when writing JSON files (write temp → replace target).
- **Cascade delete** prevents orphan records:
  - deck → cards
  - card → srs_state + reviews

---

## 🧪 Testing

### Automated Tests (pytest)

- Developed with a **test-first (TDD-style)** approach using `pytest`.
- **Total Automated Tests: 37**

| Test Suite File                   | Count | Focus                                     |
|-----------------------------------|------:|-------------------------------------------|
| `tests/test_auth.py`              |     4 | Register / login / logout                 |
| `tests/test_storage.py`           |     6 | JSON persistence, IDs, SRS/reviews writes |
| `tests/test_deck_service.py`      |     5 | Deck rules, auth requirement, isolation   |
| `tests/test_card_service.py`      |     5 | Card authorization & edge cases           |
| `tests/test_review_service.py`    |     2 | Review permissions                        |
| `tests/test_srs_service.py`       |     2 | SRS state create/update                   |
| `tests/test_review_scheduling.py` |     8 | Scheduling behavior by quality            |
| `tests/test_report_service.py`    |     1 | Due cards reporting                       |
| `tests/test_backup_service.py`    |     2 | Export/backup output                      |
| `tests/test_study_today_flow.py`  |     2 | Study Today CLI flow (E2E-style)          |

### Run All Tests
```bash
pytest -q
```

### Run Specific Test Suite - Example
```bash
pytest -q tests/test_srs_service.py
```

---

### Manual Tests

**Purpose:** Validate real user CLI flows (manual execution)

**Total Manual Test Scripts: 5** (under `manual_tests/`):
- `auth_manual.py`
- `deck_manual.py`
- `card_manual.py`
- `review_srs_manual.py`
- `backup_manual.py`

### Run a Manual Script Example
```bash
python manual_tests/review_srs_manual.py
```

- **Manual Test Cases:** 10  
  (documented in test_cases_manual.md)

**Manual Test Documents** (under `manual_tests/`):
- `test_plan_manual.md`
- `test_scenarios_manual.md`
- `test_cases_manual.md`
- `test_report_manual.md`

### Smoke / E2E Check (CLI)
- Smoke test: run the app and confirm menus work:
```bash
python main.py
```
- E2E-style automated flow is covered in:
- tests/test_study_today_flow.py

---

## 🎯 Design Decisions

### Why JSON Instead of SQLite?
- Required by the project specification (file-based persistence).
- Human-readable and easy to inspect during development and testing.
- Simplifies backup/export operations.

### Why CLI Instead of GUI?
- Focuses on core business logic and algorithms.
- Easier to test with both automated and manual tests.
- Keeps the project lightweight and dependency-free.

### Why Atomic Writes?
- Prevents JSON corruption in case of crashes or interrupted writes.
- Ensures data consistency without external database support.

---

## 👤 Author

**Ayşenur Büyümez**
- GitHub: [AysenurB01](https://github.com/AysenurB01)
- LinkedIn: [Ayşenur Büyümez](https://www.linkedin.com/in/aysenur-buyumez/)

---

## 🙏 Acknowledgments

- Project specification by **Hamit MIZRAK** (Computer Engineer)
- SM-2 algorithm by **Piotr Wozniak**

---

**Built with ❤️ using Pure Python**