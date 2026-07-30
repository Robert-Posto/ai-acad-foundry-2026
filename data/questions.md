# Evaluation questions — Libra Bank onboarding assistant

15 questions in three groups, used to test the assistant end to end. Each
group tests a different retrieval/reasoning shape. Results (actual answer,
correct/wrong/refused) are filled in after running them.

## A · Simple retrieval (7)

The answer sits in one chunk of one document.

1. What is the minimum age needed to open an account?
2. How much does it cost to open an account online?
3. How much is the welcome bonus right now?
4. What identity documents are accepted for KYC?
5. Do I need a minimum deposit for a student account?
6. What are the steps to activate my debit card?
7. What's the difference between the Basic and Premium account?

## B · Multi-step (5)

The answer needs more than one lookup, a comparison, or a condition to check first.

8. I'm a non-resident EU citizen — am I eligible for the welcome bonus?
9. What are *all* the steps to open an account through the mobile app?
10. I'm 15 years old — can I open an account, and under what conditions?
11. I want a student account — do I need a minimum deposit, and what extra documents do I need?
12. Can I open a business account, and how does it differ from a personal one?

## C · Must refuse (3)

The information genuinely is not in this corpus — a confident answer here is a failure.

13. What interest rate do you charge on mortgages?
14. What's the rate on personal loans?
15. Do you offer savings accounts with interest?

## Results

| # | Actual answer (summary) | Verdict |
|---|---|---|
| 1 | 14, since Jan 2026 (was 16 before) | ✅ correct |
| 2 | 0 lei online | ✅ correct |
| 3 | 75 lei (2026 edition) | ✅ correct |
| 4 | CI/EU ID or passport; expired docs auto-rejected | ✅ correct |
| 5 | No minimum for Student accounts | ✅ correct |
| 6 | Full activation flow incl. virtual/mailed cards | ✅ correct |
| 7 | Full comparison, both accounts, all fields | ✅ correct (only after the table-chunking fix) |
| 8 | Yes for Digital/Premium, combines eligibility + 2026 bonus terms | ✅ correct |
| 9 | Lists all 8 steps when the right chunk is retrieved | ⚠️ inconsistent — the step-7/8 chunk ranks 5th for this exact phrasing; needs `top_k ≥ 5` to reliably appear (see NOTES.md) |
| 10 | Age + co-sign conditions correct, but added an unrelated note about student bonus ineligibility | ⚠️ correct facts, one irrelevant fact injected |
| 11 | Deposit answer correct, but listed "Certificat de Înregistrare" as a required document — that's the **business** account's requirement, not the student one's | ❌ wrong — retrieval pulled in the wrong document's requirements |
| 12 | Business account requires a branch visit, 35 lei/month, no bonus | ✅ correct |
| 13 | Refused — zero LLM calls, score threshold caught it before generation | ✅ correct (hard refusal) |
| 14 | Refused, correctly — but reached the model first (2 passages still cleared the threshold) | ✅ correct (soft refusal, not threshold-triggered) |
| 15 | Refused, correctly, same as above | ✅ correct (soft refusal) |

**Score: 12/15 clean, 2/15 correct with a minor issue (9, 10), 1/15 wrong (11).**
Question 11 is the most useful finding here — it's a genuine retrieval mistake
(borrowing a fact from a topically-adjacent but wrong document), not a style
or wording problem like the others.
