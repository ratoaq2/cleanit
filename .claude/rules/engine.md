---
paths:
  - "cleanit/*.py"
---

# Rule engine

The Python engine is generic. Put cleaning behavior in `cleanit/data/`, not in Python. `Config`,
`Config.select_rules`, `Rules.apply`, and `Subtitle` are a public API that other packages use. Keep them
stable. Build `Change` objects only when debug logging is on.

Read `docs/architecture.md` before you change the engine or the CLI.
