# Admin panel — RAG Teaching API

A single-file admin console for the [RAG Teaching API](../backend/README.md). Lets
an operator check backend status, chunk and ingest text, inspect/reset the Qdrant
collection, search, and ask questions with or without RAG augmentation.

## Run it

1. Make sure the backend is running (see [`code/backend/README.md`](../backend/README.md)):
   ```bash
   cd code/backend
   docker compose up -d --build
   ```
2. Open [`index.html`](index.html) directly in a browser — no build step, no dev
   server needed (double-click it, or `start index.html` on Windows).
3. The panel defaults to `http://localhost:7799`; change the URL field at the top
   if your backend runs elsewhere.

## What it covers

| Section | Endpoint(s) |
|---|---|
| Status | `GET /health`, `GET /config` |
| Chunk | `POST /chunk` |
| Ingest | `POST /ingest` |
| Collection | `GET /collection`, `DELETE /collection` |
| Search | `POST /search` |
| Ask | `POST /ask` (toggle `use_rag`) |

Errors from the API (e.g. `409` dimension mismatch, `503` Qdrant down) are shown
as returned, not swallowed.
