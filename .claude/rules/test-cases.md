---
paths:
  - "tests/data/**"
  - "tests/test_data.py"
  - "tests/test_rule.py"
---

# Data tests

Each folder in `tests/data/cases/` is one full-pipeline case. The language comes from the file names
`input.<lang>.srt` and `expected.<lang>.srt`. The tags come from `meta.yaml`.

Read `docs/testing.md` before you add a case or change the test generation.
