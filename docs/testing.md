# Testing

There are two kinds of data tests. Both use the built-in rules.

## Rule examples

The `examples:` of each rule are test cases. `tests/test_rule.py` makes one test for each example. The
test applies only that one rule. The key is the input text, and the value is the expected text. A `null` value means that the rule removes
the entry. YAML `|` blocks keep the line breaks of a multi-line entry.

For a rule fix, add examples first. Add examples for text that the rule must not change. You do not need
new Python test code.

```bash
uv run pytest -q --tb=short tests/test_rule.py -k "some text of the example input"
```

## Full-pipeline cases

Each folder in `tests/data/cases/` is one case. `tests/test_data.py` runs `Subtitle.clean` on the input
file, with the rules of the case, and compares the result with the expected file. This checks the rule
selection by tag and language, the order of the rules, and the new entry numbers.

A case folder contains:

- `meta.yaml`: `description` (why the case exists) and `tags` (the rule tags to select).
- `input.<lang>.srt` and `expected.<lang>.srt`. The language comes from the file name, in the same way as
  for real files (`get_subtitle_language` in `cleanit/subtitle.py`). Do not add the language to
  `meta.yaml`.

The test ID is the folder name:

```bash
uv run pytest -q --tb=short tests/test_data.py -k "ocr-o2-oxygen-preserved-en"
```

To add a case, add a new folder with this layout. Use invented names and titles. Do not copy text from
real subtitles.
