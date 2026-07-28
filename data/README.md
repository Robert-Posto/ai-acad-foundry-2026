# Corpus — Libra Bank onboarding

Fifteen fictional documents describing how a customer opens and activates an
account at Libra Bank (the fictional bank used throughout this course). No
real customer data or employer documents are used anywhere in this corpus.

## Documents

| File | Topic |
|---|---|
| `account-types-comparison.md` | Table comparing the four personal account types |
| `eligibility-criteria.md` | Who can open an account: age, residency, documents |
| `required-documents-kyc.md` | Identity documents accepted for verification |
| `opening-via-mobile-app.md` | Step-by-step account opening in the app |
| `opening-in-branch.md` | Step-by-step account opening at a branch |
| `opening-fees.md` | Account opening fees and minimum initial deposit |
| `welcome-bonus-2025.md` | Welcome bonus terms, superseded edition |
| `welcome-bonus-2026.md` | Welcome bonus terms, current edition |
| `minimum-age-policy.md` | History of the minimum age requirement |
| `activating-debit-card.md` | Activating a debit card after account opening |
| `setting-up-online-banking.md` | Enabling online/app banking access |
| `student-account-onboarding.md` | Onboarding flow specific to Student accounts |
| `business-account-onboarding.md` | Onboarding flow for self-employed/business |
| `onboarding-channels-not-supported.md` | Channels Libra Bank deliberately does not offer |
| `cooling-off-and-closing.md` | The 14-day right to cancel a new account |

## Trap cases, and which document covers each

| Case | Document(s) | How |
|---|---|---|
| A precise number | `opening-fees.md` | Exact fee (0 lei online / 25 lei branch) and minimum deposit (50 lei) |
| Two documents that must be combined | `eligibility-criteria.md` + `welcome-bonus-2026.md` | "Is a non-resident EU applicant eligible for the welcome bonus?" needs both: general eligibility (who can even open an account) and the bonus's own eligibility clause |
| Near-duplicates that differ | `welcome-bonus-2025.md` vs `welcome-bonus-2026.md` | Same topic, same structure, different amount (50 vs 75 lei) and different resident restriction |
| A long procedure with steps | `opening-via-mobile-app.md` | 8 numbered steps, easy for naive chunking to cut mid-step |
| A table | `account-types-comparison.md` | Markdown table of account types and their features |
| Contradiction across versions | `minimum-age-policy.md` | Minimum age was 16 (2025), is 14 (from Jan 2026) — `effective`/`version` metadata is what resolves it |
| Something deliberately absent | `onboarding-channels-not-supported.md` | Libra Bank does not offer phone-only onboarding or third-party/agent onboarding — the assistant should say so, not invent a phone process |
