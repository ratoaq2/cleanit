---
paths:
  - "tests/**"
---

# Tests

- Bug fix: commit a failing test that shows the bug first, then the fix. See `docs/workflow.md`.
- Run with quiet flags: `uv run pytest -q --tb=short tests`.
- A rule fix: add `examples:` to the rule first, with the unchanged text too. Add a case in
  `tests/data/cases/` for a full-pipeline check. See `docs/testing.md`.
- Use invented names and titles in fixtures. Do not copy real subtitles. They are copyrighted content.
