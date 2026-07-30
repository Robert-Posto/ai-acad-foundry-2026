# Assignment 2 — Notes

## Chunk counts (folder 1 — same input text, four strategies)

| Strategy | Chunks |
|---|---|
| static | 6 |
| sentence | 5 |
| dynamic | 5 |
| semantic | 13 |

`semantic` produced more than double the others — it cuts wherever the cosine
similarity between adjacent sentences drops below the threshold, so it reacts to
every small topic shift instead of packing to a fixed size.

## Acceptance questions (Part 3)

**1. How many dimensions does an embedding have here?**
1536 — the `text-embedding-3-small` deployment. Confirmed both on `/ingest`
(`vector_dimension: 1536`) and on `/collection` (`points_count: 7`, same dimension).

**2. What score did the off-topic query get, and what does that tell you?**
0.2231 — well below the on-topic queries (0.4465 for the "frozen card"
paraphrase, 0.4792 for "early repayment"). Retrieval **always** returns the
nearest `top_k` points, whether or not they are actually relevant — nothing
stops it from returning something. The score is what tells you if the result
means anything: a low score is the signal that the corpus has nothing related
to the question, not an error condition.

**3. What exactly is added to the prompt when `use_rag` is `true`?**
A `CONTEXT — retrieved passages, most similar first:` block is prepended before
the question, listing the top-k retrieved passages each labeled `[1]`, `[2]`,
`[3]…` with their similarity score, followed by the literal question. Without
RAG, `prompt_sent` is just the question itself. The system prompt also changes
tone: with RAG it instructs the model to cite `[1]` `[2]` and say explicitly
when the passages don't cover what's needed instead of inventing an answer —
and it works: an out-of-corpus question ("student loan interest rate") got a
polite refusal explaining exactly what's missing, not a plausible invention.

**4. Where can the `lyrical` agent run, and how do you know?**
Currently `runs_on: "unknown"` for every persona, including `lyrical`. The
`/agents` response's `foundry` block gives the exact reason:
`AZURE_AI_PROJECT_ENDPOINT is not set` — so the backend can't even attempt to
query the Foundry Agent Service. Separately, the Agent Service only accepts
Microsoft Entra (identity) authentication, and this run uses `AZURE_AI_AUTH=key`
— so even with the endpoint set, running under Docker with a key would still
report `unknown`. Resolving it for real needs both: `AZURE_AI_PROJECT_ENDPOINT`
set in `.env`, and the backend run locally after `az login` (Entra auth
available), which is also the setup the local-run Agents screenshot for this
assignment requires.

## Tools (folder 6)

`Web fetch · a real site` (a Microsoft Learn docs page): `warnings` came back
empty, but `stats.signal_ratio` was only 0.0692 — over 93% of the fetched HTML
was non-content (scripts, nav, chrome), and only ~3.7KB of the ~53.6KB page was
usable text. Shows the limits of a naive scraper even when it doesn't trip a
warning outright.

---

# Assignment 3 — Project notes

## Corpus smoke test — baseline ("before" state)

15-document onboarding corpus (`data/`), loaded with `scripts/load_corpus.py`
(`dynamic` strategy) into a clean collection: 38 chunks, `points_count: 38`.
Ran 13 questions through Chat with `use_rag: true` to sanity-check the whole
pipeline before touching ingestion/retrieval improvements. 11/13 correct.

| # | Question | Verdict | Note |
|---|---|---|---|
| 1 | Account opening fee if I open online? | ✅ correct | 0 lei online, correctly adds the 50 lei min. deposit rule |
| 2 | Same fee, but "...at Banca Transilvania?" | ✅ correct | refused to answer for a bank not in the corpus, then correctly answered for Libra Bank instead — did not confuse entities |
| 3 | Minimum age to open an account? | ✅ correct | 14, cites both the current and superseded (16) policy with dates |
| 4 | Can a 15-year-old open an account? | ✅ correct | applied the **current** policy (14+), not the old 16+ one |
| 5 | How much is the welcome bonus right now? | ✅ correct | 75 lei (2026 edition) — did not pick the superseded 50 lei (2025) |
| 6 | Non-resident EU citizen, eligible for the bonus? | ✅ correct | correctly combined `eligibility-criteria.md` + `welcome-bonus-2026.md` |
| 7 | Steps to open via mobile app (persona: lyrical) | ⚠️ incomplete | lists steps 1–6, drops steps 7–8 (choose account type/bonus, wait for verification) |
| 8 | Same question (persona: default) | ⚠️ incomplete | same omission — reproducible across two different personas, not a one-off |
| 9 | Difference between Basic and Premium account? | ⚠️ incomplete | describes Basic fully, then says Premium details are "missing from the provided documents" — correctly refused to invent, but never retrieved the Premium row |
| 10 | Open an account by phone call? | ✅ correct | refuses correctly, cites the real supported channels instead |
| 11 | Interest rate on your mortgages? | ✅ correct | refuses cleanly, asks clarifying questions instead of inventing a rate |
| 12 | Minimum deposit for a student account? | ✅ correct | no minimum, correctly adds the guardian co-signature note for minors |

## Known issues found (before any Part 4/5 improvements)

**1. Multi-step procedures get truncated, not cut by chunking.**
`/search` on question 7/8 shows all three chunks of
`opening-via-mobile-app.md` were retrieved (scores 0.65 / 0.63 / 0.58) — the
chunk holding steps 7–8 (0.5848) is in the top-4, so retrieval did its job.
The `default` persona's style rule *"two short paragraphs maximum"* makes
generation drop the tail of the list to stay short — and spends the freed-up
space on an unrequested extra fact instead of finishing the procedure. This
is a **generation** problem, not a chunking one, and it reproduces with the
`lyrical` persona too, so it isn't persona-specific.

**2. The comparison table gets split, so Premium answers are refused.**
`account-types-comparison.md` is one Markdown table; the naive chunker splits
it so the Basic row ends up in a different chunk than the Premium row. Asked
to compare the two, the assistant correctly refuses to invent Premium's fee
(no hallucination — the "never invent" rule works), but the answer is only
half useful. This is exactly the table-chunking failure predicted when the
corpus was designed, now confirmed with a real question.

Both are strong candidates for the required Part 4/5 improvements: #4
("never split a table") directly fixes issue 2; issue 1 needs either a
generation-side fix (loosen the paragraph limit for enumerated-step answers)
or a retrieval-side one (re-ranking, so the tail chunk doesn't lose to a
tangential one).

## Custom agent: `onboarding` persona

Added `app/agents/personas/onboarding.json` — a persona built specifically
for this project's corpus (not a generic bank assistant), with style rules
targeting the two issues found above directly: never summarize a numbered
procedure, state exact figures, and be explicit about what's missing when
comparing products.

Re-ran both broken questions with `agent: "onboarding"`:

- **Steps question — fixed.** All 8 steps now come back in full, in order,
  nothing dropped. Confirms issue 1 was a generation-side problem (the
  `default` persona's "two short paragraphs" rule), not a retrieval one —
  fixing the prompt/persona was enough, no ingestion change needed.
- **Basic vs Premium — still incomplete, as expected.** The persona is now
  much more transparent (explicitly separates "Facts about Basic" / "Facts
  about Premium" / "What is missing" instead of a vague refusal), but still
  cannot state Premium's fee/card/withdrawals/overdraft, because retrieval
  still never surfaces that row. This confirms issue 2 is a genuine
  retrieval/ingestion problem — a better persona cannot fix it, only
  improvement #4 (never split a table) can.

## Ingestion improvement #4: never split a table

**Before:** `chunk_dynamic` (`app/chunking.py`) splits text into paragraphs,
then sentences. A Markdown table has no sentence-ending punctuation, so the
whole table was seen as one oversized "sentence" and fell into the
hard-split-on-raw-characters fallback — severing rows mid-cell.
`account-types-comparison.md` came out as 4 chunks, with the Basic and
Premium rows landing in different ones.

**Fix:** added `is_markdown_table()` — a block counts as a table when every
non-blank line matches `| ... |`. `chunk_dynamic` now detects a table
paragraph before the sentence-splitting logic and emits it as one atomic
chunk, never hard-split, even past the normal size budget.

**After, measured:**
- `account-types-comparison.md`: 4 chunks → **3 chunks** (intro / whole table,
  601 chars / trailing paragraph). The table is never split again, regardless
  of how long it is.
- Whole corpus: 38 chunks → **37 chunks** after a clean re-ingest (one fewer,
  matching the table document's change).
- Same "Basic vs Premium" question, re-asked after re-ingesting: the
  assistant now states fee, card type, ATM withdrawals *and* overdraft limit
  for **both** accounts, all cited from the single table chunk — no more
  "Premium details are missing from the provided documents."

## Two more ingestion improvements + two retrieval improvements

### Ingestion #1 — stable chunk ids (`app/vectorstore.py`)

**Before**: every ingest generated fresh `uuid4()` ids, so re-running the
loader on an unchanged corpus silently duplicated every point (hit this
directly: 38 → 46 points after a second run in the middle of testing).

**Fix**: ids are now derived deterministically from `source + chunk index`
(`uuid5`), so the same document always maps to the same ids.

**After, measured**: ran `scripts/load_corpus.py` twice in a row on a clean
collection — `points_count` stayed at **37 both times** (would have been 74
under the old behaviour).

### Ingestion #2 — real metadata in the payload (`app/vectorstore.py`, `scripts/load_corpus.py`)

**Before**: every document's front matter (`title`, `product`, `audience`,
`effective`, `version`) was parsed by the loader just to print a nicer log
line, then thrown away — none of it reached Qdrant.

**Fix**: `/ingest` now accepts these fields and stores them in each point's
payload; `/search` and `/ask` return `effective`/`version` on every hit.

**After**: `welcome-bonus-2025.md` is now marked `superseded: true` in its
own front matter — the one flag that makes retrieval improvement #2 below
possible at all.

### Retrieval #2 — metadata filter, exclude superseded documents (`app/main.py`, `app/vectorstore.py`)

**Before**: `welcome-bonus-2025.md` and `welcome-bonus-2026.md` competed on
cosine score alone for the query "how much is the welcome bonus" — measured
**2025 scoring 0.5891, actually higher than 2026's 0.5570**. Without the
fix, the *expired* terms would have won the top slot on a plain top-k search.

**Fix**: `/search` and `/ask` now exclude points with `superseded: true` by
default (`exclude_superseded`, via a Qdrant payload filter); an
`include_superseded` flag brings the old behaviour back on request, for
comparison.

**After, measured**: same query, default settings — only `welcome-bonus-2026`
chunks are returned. With `include_superseded: true`, the 2025 chunk
reappears and outscores 2026 again (0.5891 vs 0.5570), confirming the
filter — not luck — is what fixes it.

### Retrieval #1 — score threshold (`app/main.py`, `app/config.py`)

**Before**: retrieval always returns its top-k regardless of relevance
(measured at Assignment 2: on-topic queries score ~0.44–0.65, off-topic
~0.22). Whether a weak match got rejected depended entirely on the LLM
noticing and refusing — a persona-level behaviour, not a system guarantee.

**Fix**: `SCORE_THRESHOLD` (default `0.32`, chosen between the two measured
ranges) drops hits below the floor in both `/search` and `/ask`. In `/ask`,
if nothing clears the bar, the endpoint answers "I don't have anything
relevant to that in the knowledge base" directly — **no LLM call is made**.

**After, measured**: asked "What interest rate do you charge on mortgages?"
(off-topic for this onboarding corpus) — response came back with
`provider: "none"`, `model: "none"`, `usage: null` — a guaranteed, free,
instant refusal instead of a hopeful one. A normal on-topic question
("minimum age to open an account?") was unaffected — still answered
normally with 4 retrieved passages.
