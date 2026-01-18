# StudyBuddy – Manual Test Scenarios

## 1. Authentication Scenarios
- User registers with valid credentials
- User cannot register with an existing email
- User logs in with valid credentials
- User cannot log in with invalid credentials
- Logged-in user logs out successfully

---

## 2. Deck Management Scenarios
- User creates a new deck
- User lists only their own decks
- User deletes an existing deck
- Deleting a deck removes its cards (cascade delete)
- User cannot delete another user's deck

---

## 3. Card Management Scenarios
- User creates a card in a selected deck
- User views cards belonging to a deck
- User updates an existing card
- User deletes a card
- User cannot access cards from another user's deck

---

## 4. Study Today (SRS) Scenarios
- System shows due cards for today
- System shows message when no cards are due
- User reviews a card with quality score (0–5)
- Next due date is updated after review
- Low quality review resets repetition and interval

---

## 5. Reports Scenarios
- User views due cards report
- User views last 7 days review activity
- User views overall study statistics

---

## 6. Backup / Export Scenarios
- User exports backup successfully
- Backup file is created with timestamp
- Backup contains users, decks, cards, SRS states and reviews

---

## 7. Negative and Edge Case Scenarios
- User attempts actions without login
- User enters invalid menu options
- User enters invalid quality score during review
