# StudyBuddy – Manual Test Plan

## 1. Introduction
This document describes the manual testing strategy for the **StudyBuddy CLI Application**.

StudyBuddy is a command-line based flashcard and spaced repetition system (SRS)
that allows users to manage decks, cards, perform daily study sessions,
view reports and export backups.

This test plan defines:
- What will be tested
- How it will be tested
- Scope and limitations of manual testing

---

## 2. Objectives
The objectives of manual testing are:

- Verify core business flows work correctly
- Validate CLI-based user interaction
- Ensure authentication and authorization rules are enforced
- Verify SRS scheduling behavior
- Confirm reporting and backup accuracy
- Detect functional and usability issues

---

## 3. Scope of Testing

### 3.1 In Scope
Manual testing covers:

- Authentication
  - Register
  - Login
  - Logout

- Deck Management
  - Create deck
  - List decks
  - Delete deck (including cascade delete of cards)

- Card Management
  - Create card
  - List cards
  - Update card
  - Delete card

- Study Today (SRS)
  - Due card detection
  - Review flow
  - Quality input handling (0–5)
  - Scheduling logic

- Reports
  - Due cards today
  - Last 7 days activity
  - User statistics

- Backup / Export
  - JSON backup creation
  - Backup file structure

---

### 3.2 Out of Scope
The following are not covered by this manual test plan:

- Performance testing
- Load or stress testing
- Security / penetration testing
- Automated testing (covered separately by pytest)
- UI/UX testing beyond CLI usability

---

## 4. Test Approach
Manual testing is performed using:

- CLI interaction via terminal
- Black-box testing techniques
- Functional testing
- Positive and negative test scenarios

Execution order:
1. Test Plan
2. Test Scenarios
3. Test Cases
4. Test Report

---

## 5. Test Environment
- OS: Windows
- Python Version: Python 3.14
- Interface: Command Line Interface (CLI)
- Data Storage: JSON files
- Version Control: Git

---

## 6. Entry Criteria
Manual testing starts when:

- Application runs without syntax errors
- Core services are implemented
- Storage initializes successfully
- CLI menus are accessible

---

## 7. Exit Criteria
Manual testing is complete when:

- All planned test cases are executed
- No critical defects remain unresolved
- Test report is prepared
- Backup functionality is verified

---

## 8. Roles & Responsibilities
- **QA Tester**
  - Prepare test plan
  - Execute manual tests
  - Report defects

- **Developer**
  - Fix reported defects
  - Maintain codebase

---

## 9. Test Deliverables
- test_plan_manual.md
- test_scenarios_manual.md
- test_cases_manual.md
- test_report_manual.md

---

## 10. Risks & Mitigation
- CLI input errors  
  → Input validation and error handling applied

- JSON data corruption  
  → Atomic write mechanism used

- Incomplete coverage  
  → Structured test scenarios defined

---

## 11. Approval
This test plan is prepared for educational and portfolio purposes
and follows manual QA best practices.
