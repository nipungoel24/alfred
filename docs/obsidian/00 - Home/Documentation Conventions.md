---
type: architecture
layer: meta
status: active
tags:
  - documentation
---

# Documentation Conventions

## Curated vs Generated

- **Curated** notes (everything outside `99 - Generated`) are written by engineers and explain *why*: architecture, tradeoffs, security rationale, runtime behavior. Edit freely.
- **Generated** notes (inside `99 - Generated`) are written by `py tools/docs/generate_knowledge_graph.py` and explain *what*: symbols, signatures, call edges, schema facts. Regenerate with the tool — never hand-edit; the next run overwrites them.

## Frontmatter

Every note carries YAML frontmatter with at least `type`, `status`, and `tags`. `generated: true` marks generated notes. Symbol notes additionally carry `qualified_name`, `source` (repo-relative), and `line`.

## Relationship Sections

Use consistent section names so the graph reads the same everywhere: `Calls` / `Called By` / `Reads` / `Writes` / `Produces` / `Consumes` / `Uses` / `Implements` / `Rendered By` / `Tested By` / `Related`.

## Wikilinks

- Link any implementation target: `[[POST --api-accounts-{account_id}-sync|sync_account]]`, `[[table_emails]]`, `[[frontend.src.mail.MailWorkspace.MailWorkspace]]`.
- Alias for readability: `[[backend.app.main.sync_account|sync_account]]`.
- Link curated notes by title: `[[System Architecture]]`.
- Endpoint notes use their generated filename form: `[[POST --api-accounts-{account_id}-sync]]`.

## Small Function Policy

The generator documents **nearly every named function and method**, including small helpers, because graph edges are the product. Exceptions: anonymous callbacks, `__pycache__` artifacts, and magic methods where they add no edge. If a function exists but its note is trivial, that is intentional — the edge is the value.

## Source Links

Always repo-relative: `backend/app/ai/service.py:122`. Never absolute machine paths.

## Secrets

Never write actual values. Document variable names and purpose only — see [[Environment Variables]] and [[Token Security]]. Run `py tools/docs/validate_vault.py` before committing.
