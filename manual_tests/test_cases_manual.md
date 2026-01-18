# StudyBuddy – Manual Test Cases

## TC-01: Successful User Registration
- Preconditions:
  - User is on the main menu
- Steps:
  1. Select "Register"
  2. Enter a valid email, password and name
- Expected Result:
  - User is registered successfully
  - Success message is displayed

---

## TC-02: Login with Valid Credentials
- Preconditions:
  - User is already registered
- Steps:
  1. Select "Login"
  2. Enter correct email and password
- Expected Result:
  - User is logged in
  - Main menu is displayed

---

## TC-03: Login with Invalid Password
- Preconditions:
  - User is registered
- Steps:
  1. Select "Login"
  2. Enter valid email and incorrect password
- Expected Result:
  - Login is rejected
  - Error message is displayed

---

## TC-04: Create Deck
- Preconditions:
  - User is logged in
- Steps:
  1. Go to Deck Menu
  2. Select "Create Deck"
  3. Enter a deck name
- Expected Result:
  - Deck is created successfully
  - Deck appears in deck list

---

## TC-05: Create Card
- Preconditions:
  - User is logged in
  - At least one deck exists
- Steps:
  1. Select a deck
  2. Choose "Create Card"
  3. Enter front and back text
- Expected Result:
  - Card is created
  - Card is listed under the selected deck

---

## TC-06: Update Card
- Preconditions:
  - Card exists in a deck owned by the user
- Steps:
  1. Select a deck
  2. Select a card
  3. Choose "Edit Card"
  4. Update front and/or back text
- Expected Result:
  - Card content is updated successfully

---

## TC-07: Review Card with High Quality
- Preconditions:
  - User is logged in
  - Card exists and is reviewable via Study Today flow
- Steps:
  1. Open "Study Today"
  2. Review the card with quality score 5
- Expected Result:
  - Review is saved
  - SRS state is updated
  - Next due date is scheduled in the future

---

## TC-08: Review Card with Low Quality
- Preconditions:
  - User is logged in
  - Card exists and is reviewable
- Steps:
  1. Review the card with quality score 1
- Expected Result:
  - Review is saved
  - Repetition counter is reset
  - Due date is scheduled for the next day

---

## TC-09: View User Statistics
- Preconditions:
  - User has at least one completed review
- Steps:
  1. Open Reports Menu
  2. Select "User Statistics"
- Expected Result:
  - Correct totals and average quality are displayed

---

## TC-10: Export Backup
- Preconditions:
  - User is logged in
- Steps:
  1. Select "Backup / Export" from main menu
- Expected Result:
  - Backup file is created in `backups/` directory
  - File name contains a timestamp
  - Backup includes users, decks, cards, SRS states and reviews
