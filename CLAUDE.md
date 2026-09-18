# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CleanIt is a CLI tool (and small library) that cleans subtitle (`.srt`) files: fixing common OCR
errors, tidying formatting/spacing, and stripping SDH descriptions, lyrics, ads/spam, and font-style
tags. Almost all of its behavior lives in declarative YAML rule files, not in Python code — the
Python code is a thin, generic engine that loads and applies those rules.

## Commands

Dependency management and running things is done via `uv`.

```bash
uv sync --locked --all-groups        # install/sync dependencies (matches CI)

# tests
bash scripts/test.sh                                  # what CI runs: verbose + coverage
uv run pytest tests/                                  # quick run
uv run pytest tests/test_rule.py                      # rule-example tests only
uv run pytest tests/test_data.py                       # fixture/case tests only
uv run pytest tests/test_data.py -k "case-slug"        # a single fixture case (see below)
uv run pytest tests/test_rule.py -k "some snippet of the example's input text"  # a single rule example

# lint / type-check (all part of CI's `lint` job)
uv run ruff check .
uv run ruff format --check .          # add --fix / drop --check to auto-fix
uv run mypy cleanit

# run the CLI locally without installing
uv run cleanit --help
uv run cleanit -t ocr -t no-sdh -t tidy -l en -l pt-BR /path/to/subtitles
uv run cleanit -t default --test --debug some.srt   # dry run with verbose per-file logging
```

CI (`.github/workflows/test.yml`) runs the `test` job (via `scripts/test.sh`) across Python
3.10–3.14, and a separate `lint` job running ruff check, ruff format --check, and mypy on `cleanit`.

## Architecture

### The rule engine is generic; the actual subtitle-cleaning logic is data

`cleanit/rule.py`, `cleanit/config.py`, and `cleanit/subtitle.py` implement a generic
"select rules by tag/language, apply regexes in priority order" engine. All of the actual
OCR-fix/tidy/SDH-removal/lyrics-removal/spam-removal logic lives in YAML under `cleanit/data/`,
loaded automatically at import time as the built-in rule set. Adding or fixing subtitle-cleaning
behavior almost always means editing a YAML file there, not the Python engine.

- `cleanit/data/cleanit.yml` — shared `aliases` (regex character-class shortcuts like
  `[:upper:]`, `[:vowel:]` expanded by string substitution before compiling).
- `cleanit/data/cleanit-ocr*.yml`, `cleanit-tidy*.yml`, `cleanit-no-sdh.yml`, `cleanit-no-lyrics.yml`,
  `cleanit-no-spam*.yml`, `cleanit-no-style.yml` — the rule sets themselves. Files with a language
  suffix (`.en.yml`, `.pt.yml`, `.de.yml`) only apply to that language; files without one apply to
  all languages. `cleanit/data/__init__.py` lists every file that gets loaded by default
  (`default_config_resources`) — a new data file must be added there to take effect.
- Each rule uses YAML anchors (`<<: *ocr`) to inherit shared `tags`/`priority`/`languages` from a
  `templates` block at the top of its file.
- Rules are validated against a JSON Schema (`cleanit/schema.py`) on load
  (`utils.validate`/`load_config_resource`/`load_config_file`).

### Rule semantics worth knowing before editing a pattern

- A rule's `patterns` are plain Python `re` patterns (not full multiline text — see below), tried
  in order; the first one that matches wins for that pass, and matching repeats until no rule
  matches or the text vanishes (`Rule.apply` / `Rules.apply` in `cleanit/rule.py` recurse until
  stable).
- **A rule is applied to `item.text` of one SRT entry, which is the *entire* (possibly multi-line)
  dialogue block joined with `"\n"`** — not one physical line at a time. This matters a lot: a
  pattern using `\s*`/`\s+` will happily match *across* the newline between two separate lines of
  the same subtitle entry, silently merging unrelated lines/words. If a fix is only meant to close
  a gap inside a single (broken) word, don't use bare `\s`; something crossed a line/word boundary
  is a real bug, not just an edge case — this exact mistake has caused real content corruption
  before (see `fix-broken-c-cedilla[ocr:pt]` history and its regression test).
- Rule `tags` select which rule sets run (`ocr`, `tidy`, `no-sdh`, `no-lyrics`, `no-spam`,
  `no-style`, and the umbrella `minimal` = ocr+tidy, `default` = everything except `no-style`).
  Rule `languages` (IETF codes) are matched via language *groups* (base language, ignoring region —
  see `get_language_groups` in `cleanit/utils.py`), so a `pt`-tagged rule applies to `pt-BR` files
  too; a rule with no `languages` applies to every language.
- Every rule's `examples:` mapping (`input: expected_output`, YAML `|` literal blocks preserve
  embedded newlines) is *itself* a test case — `tests/test_rule.py` auto-generates one
  `pytest.mark.parametrize` case per example straight from the loaded rule set. When fixing or
  narrowing a rule, add examples there (including negative/unchanged-text examples) rather than
  writing bespoke test code — this is the fast, low-ceremony way to pin down regressions.
- Prefer narrow, word-list-style patterns (see e.g. `fix-l-to-i-words[ocr:pt]`,
  `replace-0-to-o-common-words[ocr:en]`) over broad character-class patterns for anything that
  could plausibly collide with real words/names — broad patterns like "any capital V between two
  lowercase letters" or "any O followed by digits" have historically mangled real proper nouns
  (`TiVo`, `DeVille`) and real content (`O2` the gas) respectively. Correctness on real dialogue
  beats recall on OCR artifacts.

### End-to-end test fixtures (`tests/data/cases/`)

Beyond per-rule `examples:`, there are full round-trip fixtures that run `Subtitle.clean()` (the
whole pipeline: rule selection by tag+language, applying rules entry-by-entry, re-indexing) against
a small multi-entry `.srt` and compare it to an expected output. Each case is a self-contained
directory under `tests/data/cases/<slug>/`:

- `meta.yaml` — `description` (why this case exists) and `tags` (which rule tags to select).
- `input.<lang>.srt` / `expected.<lang>.srt` — the language is read from the filename itself,
  exactly the way `Subtitle`/`get_subtitle_language` do for real files (see `cleanit/subtitle.py`),
  so there's a single source of truth and no metadata to drift out of sync.

`tests/test_data.py` discovers these by globbing `tests/data/cases/*/meta.yaml`; the pytest ID for
each case is the directory name (e.g. `test_data_files[ocr-o2-oxygen-preserved-en]`). To add a new
regression case, create a new directory following that layout — don't add a fifth flat file to the
old `tests/data/` root, and don't use real movie/show names in fixture content (use invented
names/titles instead).

### CLI (`cleanit/cli.py`)

Thin `click` wrapper: scans path(s) for `.srt` files, filters by language (`-l`) and age (`-a`),
selects rules by tag (`-t`, required), then for each collected `Subtitle` calls `.clean()` and
`.save()` unless `--test` (dry run) is passed. `--debug`/`-v` control whether rule-level match
details are logged (see `Change`/`Changes` in `cleanit/rule.py`, only built when debug logging is
enabled, to avoid the bookkeeping cost otherwise).
