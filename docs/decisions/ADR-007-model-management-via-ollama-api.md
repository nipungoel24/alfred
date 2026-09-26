# ADR-007 — Model management is built on Ollama's own API

Status: Accepted
Date: 2026-09-26
Gate: 0

## Context

Alfred requires a local model and today assumes one exists. The README tells the user to
install Ollama and run `ollama pull qwen3:4b` by hand. That is a manual procedure, not
product onboarding, and it is the largest gap between Alfred and a product someone else
could install.

`docs/PRD.md` §10 requires a real first-run model flow with states
`MODEL_RUNTIME_MISSING`, `MODEL_RUNTIME_STARTING`, `MODEL_DOWNLOAD_REQUIRED`,
`MODEL_DOWNLOADING`, `MODEL_READY`, `MODEL_FAILED`, showing real progress, real size,
disk requirement, cancel, and resume.

`backend/app/ai/supervisor.py` already detects availability and can start a found
`ollama.exe`, but it has no ability to list what is installed or to pull anything.

## Decision

Alfred manages models through Ollama's own HTTP API. It does not vendor, download, or
proxy model weights, and it does not implement a model registry.

The relevant endpoints are:
- `GET /api/tags` — list installed models. Already used by `AISupervisor._tags()`
- `POST /api/pull` — stream a download. Returns newline-delimited JSON with per-layer
  `status`, `digest`, `total`, and `completed` byte counts
- `GET /api/version` — runtime version, used to decide whether `/api/pull` streams
  progress or returns a single terminal response

Rules:
1. **Progress is computed from the byte counts Ollama reports.** Never simulated, never
   smoothed into a fake percentage. A fake progress bar is a release blocker under
   `docs/Rules.md` §1.8.
2. **Cancellation** is a dropped request plus an explicit state transition to
   `MODEL_FAILED` with a retry affordance. Ollama may leave a partial blob; Alfred
   reports the state honestly rather than claiming a clean rollback it cannot verify.
3. **Disk space is checked before starting**, using the model size Ollama reports, with
   headroom. Alfred does not guess a model size.
4. **The model is user-selectable** and persisted, replacing the build-time constant.
   The default stays `qwen3:4b`.
5. **Alfred never blocks on model work.** A missing or downloading model downgrades AI
   features and leaves the mailbox fully usable — the existing supervisor state machine
   already behaves this way and that behaviour is preserved.

## Consequences

- Ollama remains a prerequisite, which is consistent with `docs/PRD.md` §13 non-goal 4
  and with the privacy model: a bundled model would mean shipping weights
- Model setup becomes a product surface with real states, so it needs real tests, which
  means an Ollama interface abstraction so tests can drive a fake
- The AI supervisor grows a second responsibility (provisioning alongside supervision).
  If it becomes unwieldy, split it into `supervisor` and `provisioner` — do not let one
  class do both

## Rejected

**Ship the model inside the installer.** Rejected: `qwen3:4b` is multiple gigabytes. It
would make the installer unusable and would mean redistributing model weights with their
own licence obligations.

**Use llama.cpp or a bundled GGUF instead of Ollama.** Rejected: it would replace a
working, tested AI path and lose `keep_alive`, structured `format` output, and the
supervisor's auto-start. Not justified by any measured need.

**Require the user to configure the model manually and just detect it.** Rejected: this
is the current state, and it is the gap.

**Verify the download by checking the file size afterwards.** Rejected: a partial blob
can coincidentally match an expected size after a resume. Ollama's per-layer digest and
byte accounting is the only trustworthy signal available.
