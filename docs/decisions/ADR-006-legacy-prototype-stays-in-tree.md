# ADR-006 — Legacy Streamlit prototype stays in-tree, marked as legacy

Status: Accepted
Date: 2026-09-26
Gate: 0

## Context

The repository root contains a complete, pre-Alfred application: a Streamlit UI, a
LangGraph agent pipeline, a Groq-backed LLM client, and a CSV data loader.

| Path | Size | Contents |
| --- | --- | --- |
| `src/` | 6 files, 48 981 B | `app.py`, `agents.py`, `email_processor.py`, `utils.py`, `logger.py`, `__init__.py` |
| `config/` | 2 files | `settings.py` exposing `GROQ_API_KEY` and `ChatGroq` |
| `run_app.py` | 469 B | Streamlit launcher, referenced by zero code |
| `requirements.txt` (root) | 696 B | streamlit, langchain, langgraph, langchain-openai, langchain-google-genai |
| `tests/` (root) | 1 file | `test_utils.py`, imports `src.utils` and `config.settings` |
| `Data_clean/`, `data/` | 5 files | ~82 kB of sample CSV, two near-duplicates of each other |

`docs/Rules.md` §2.9 in the master requirements and `docs/Rules.md` §1.15 here both say
legacy code must not be deleted automatically, and `README.md:477` already documents its
status correctly.

## Evidence that it is genuinely dead

A scoped search across `backend/`, `frontend/`, `desktop/`, and `tools/` for imports of
`src.*`, `config.settings`, `data_loader`, `streamlit`, `langgraph`, `langchain`, and
`groq` returned **zero matches**. The only hits in modern directories are
`from backend.app import config`, which is the current config module.

The legacy cluster is a closed island. Its only inbound edge is `tests/test_utils.py`,
which nothing runs. `run_app.py` is referenced by no code at all — only by four
documentation files.

`tools/docs/docs_config.toml:25-27` already excludes `src`, `config`, and `Data_clean`
from the knowledge-graph generator, with an inline comment identifying them as the legacy
prototype.

## Decision

Keep the code. Mark it clearly. Do not let it be mistaken for a runtime path.

In Phase 3:
1. Add a `LEGACY — DO NOT USE` header to every file in `src/`, `config/`, `Data_clean/`,
   `run_app.py`, and the root `requirements.txt`
2. Add `src/README.md` explaining what it is, when it was superseded, and that it is kept
   for history only
3. Leave `tests/test_utils.py` in place; it documents the old prototype's behaviour
4. Do **not** delete any of it in this cycle

## Consequences

- The knowledge-base generator already excludes it, so the Obsidian vault stays clean
- No modern build, test, or packaging path touches it
- A future contributor who greps for `ChatGroq` finds it only here, and this file
  explains why

## The case for deleting it, stated fairly

82 kB of dead code plus 42 kB of sample CSV is real clutter. The counter-argument is
history: this repository's git log shows the Streamlit prototype becoming FastAPI, and
that transition is the single most useful piece of context for anyone reading the
project. Deleting it would also delete the only record of *why* the modern architecture
looks the way it does.

If the owner prefers deletion, that is a defensible call. It must be a single commit that
removes the whole island and updates `README.md:477`, `docs/obsidian/00 - Home/Project
Status.md:52`, `docs/obsidian/16 - Code Map/Entry Points.md:29`, and the ignore list in
`tools/docs/docs_config.toml`. It is not a phase-gated requirement either way.
