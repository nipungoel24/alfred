---
type: architecture
layer: frontend
status: active
tags:
  - frontend
---

# Settings Screen

[[frontend.src.features.settings.SettingsPage.SettingsPage|SettingsPage]] — preferences and honest runtime info.

- **Appearance** — theme segmented control (System/Light/Dark) via [[frontend.src.theme.ThemeToggle.ThemeToggle|ThemeToggle]]; persisted in localStorage, resolved pre-paint ([[frontend.src.theme.ThemeProvider.ThemeProvider|ThemeProvider]]).
- **Local AI** — model (qwen3:4b), runtime (Ollama local), live readiness from [[GET --health]].
- **Data** — storage location (AppData SQLite), DPAPI-encrypted credentials.
- **Privacy** — "All processing stays local".

## Related

- [[Model Configuration]]
- [[Environment Variables]]
- [[Design System]]
