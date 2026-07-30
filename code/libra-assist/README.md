# Libra Assist — console

A custom conversational frontend for the Libra Bank onboarding assistant — a
single self-contained HTML file, no build step, no framework, built from
scratch (different from the course's React console in `code/frontend/`).

## Run it

1. Make sure the backend is running:
   ```bash
   cd code/backend
   docker compose up -d --build      # or: uv run uvicorn app.main:app --reload --port 7799
   ```
2. Open `index.html` directly in a browser (double-click it, or `start index.html`
   on Windows) — or serve it with any static server, e.g.:
   ```bash
   python -m http.server 7800
   ```
   (useful if you want it on the same port the course console normally uses —
   stop that container first with `docker stop rag-console`).
3. The panel defaults to `http://localhost:7799` for the backend — change the
   URL under the ⚙ settings button if it runs elsewhere.

## What it does

- Each agent/persona is a separate "contact" you pick from a dropdown, with
  its own color identity.
- Multiple separate conversations per persona, with a history list — start a
  new one any time, switch back to an old one, saved in `localStorage` (so it
  survives a page refresh).
- Toggle between running the agent **locally** or via the **Azure Foundry**
  Agent Service, per message.
- RAG on/off, `top_k`, and fact-checking are tucked behind the ⚙ settings
  button rather than cluttering the chat.
- Sources are shown as citation chips with scores; answers that don't clear
  the score threshold are visually flagged as a refusal, not a normal answer.
- A 🔊 button reads any message (yours or the assistant's) aloud via Azure
  Speech; each response also shows token usage and a link to the exact prompt
  sent to the model.

## Known gaps

- Not wired into `docker-compose.yml` — running it means manually starting
  it as above, it doesn't come up with `docker compose up`.
- No automated tests; everything here was checked manually against the
  running backend.
