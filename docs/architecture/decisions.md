# Decisions

- **FastAPI + SQLite:** simple typed local API and durable storage for one Windows user.
- **Ollama / qwen3:4b:** all production inference is local and model name has one configurable source (`OLLAMA_MODEL`). There is no cloud fallback.
- **One-pass analysis:** one schema-validated Ollama call creates an email analysis. Drafts are a separate explicit call.
- **Cache:** SHA-256 of normalized sender, subject, body and date is paired with model and schema version; any mismatch re-analyzes.
- **Briefing:** an Ollama schema-validated synthesis consumes compact individual analyses, never the entire raw mailbox. Its headline counters are recomputed locally for accuracy.
- **Tauri:** a minimal desktop shell targets Windows; backend sidecar wiring remains the packaging integration point.
