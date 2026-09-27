---
paths:
  - "cleanit/data/**"
  - "cleanit/schema.py"
---

# Rule data

- A pattern sees all lines of one subtitle entry, joined with `"\n"`. Do not use a bare `\s` inside a word.
- Use a list of words, not a broad character class. Correct dialogue is more important than more OCR fixes.
- Add `examples:` for the text to change and for the text to keep. Add a new file to `cleanit/data/__init__.py`.

Read `docs/rules.md` before you change a rule. For a broad change, also read `docs/rule-validation.md`.
