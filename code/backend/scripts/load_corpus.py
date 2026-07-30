"""Load the onboarding corpus in data/ into the running RAG API, one document
at a time, instead of pasting each one into the console by hand.

    uv run python scripts/load_corpus.py

Reads every .md file in ../../data (repo root), strips its YAML front matter,
and POSTs the body to /ingest with source=<filename without extension>.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
import yaml

API_BASE = os.environ.get("API_BASE", "http://localhost:7799")
STRATEGY = "dynamic"

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def split_front_matter(raw: str) -> tuple[dict, str]:
    """Return (metadata, body) — metadata is {} if there is no --- block."""
    if not raw.startswith("---"):
        return {}, raw.strip()
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw.strip()
    _, front_matter, body = parts
    meta = yaml.safe_load(front_matter) or {}
    return meta, body.strip()


def main() -> None:
    if not DATA_DIR.is_dir():
        sys.exit(f"No data/ directory found at {DATA_DIR}")

    files = sorted(p for p in DATA_DIR.glob("*.md") if p.name.lower() != "readme.md")
    if not files:
        sys.exit(f"No .md documents found in {DATA_DIR} (besides README.md)")

    print(f"Found {len(files)} documents in {DATA_DIR}\n")

    total_chunks = 0
    with httpx.Client(base_url=API_BASE, timeout=60.0) as client:
        for path in files:
            source = path.stem
            meta, body = split_front_matter(path.read_text(encoding="utf-8"))
            if not body:
                print(f"  skip  {source} (empty body)")
                continue

            effective = meta.get("effective")
            resp = client.post("/ingest", json={
                "text": body, "strategy": STRATEGY, "source": source,
                "title": meta.get("title"),
                "product": meta.get("product"),
                "audience": meta.get("audience"),
                "effective": str(effective) if effective is not None else None,
                "version": meta.get("version"),
                "superseded": bool(meta.get("superseded", False)),
            })
            if resp.status_code != 200:
                print(f"  FAIL  {source} -> {resp.status_code} {resp.text[:200]}")
                continue

            data = resp.json()
            total_chunks += data["count"]
            title = meta.get("title", source)
            print(f"  ok    {source:<35} {data['count']} chunks  ({title})")

    print(f"\nDone — {total_chunks} chunks ingested from {len(files)} documents.")


if __name__ == "__main__":
    main()
