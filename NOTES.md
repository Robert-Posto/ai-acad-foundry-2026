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
