# Rules

The built-in rules are YAML files in `cleanit/data/`. `cleanit/schema.py` defines the file format, and
cleanit validates each file when it loads it.

## Files

- `cleanit/data/cleanit.yml` has the shared `aliases`. An alias is a short name for a regex character
  class, for example `[:upper:]` or `[:vowel:]`. cleanit replaces each alias in a `regex` pattern before
  it compiles the pattern.
- The other files hold the rules. The file name gives the tag and the language:
  `cleanit-<tag>.yml` applies to all languages, and `cleanit-<tag>.<lang>.yml` applies to one language.
- cleanit loads only the files that `default_config_resources` in `cleanit/data/__init__.py` lists. Add
  each new file to that list.

## Rule format

```yaml
templates:
  - &ocr
    tags: [ocr, minimal, default]
    priority: 10000
    languages: en

rules:
  replace-l-to-I-character[ocr:en]:
    <<: *ocr
    patterns: '\bl\b'
    replacement: 'I'
    examples:
      ? |
        And if l refuse?
      : |
        And if I refuse?
```

- A rule gets its shared `tags`, `priority`, and `languages` from a template (`<<: *ocr`).
- The rule name has the form `<name>[<tag>:<lang>]`, for example `fix-l-to-i-words[ocr:pt]`.
- The other fields are `type` (`regex` or `text`), `match`, `flags`, `disabled`, and `examples`. The
  schema in `cleanit/schema.py` lists the values.

## How cleanit applies the rules

- cleanit applies the rules to one subtitle entry at a time.
- The text of an entry is **all its lines, joined with `"\n"`**. A pattern sees the full entry, not one
  line.
- The rules run in priority order, highest first. The first rule that matches changes the text. Then
  cleanit starts again with the first rule. It stops when no rule matches, or when the text is empty.
- In a rule, the patterns run in order. The first pattern that matches replaces the text.
- A rule without `replacement` removes the full entry when it matches.
- `tags` select the rules: `ocr`, `tidy`, `no-sdh`, `no-lyrics`, `no-spam`, `no-style`. `minimal` and
  `default` are also tags. Each template adds them to its rules: `minimal` is on the `ocr` and `tidy`
  rules, and `default` is on all rules except `no-style`. The tag `all` selects every rule.
- `languages` are IETF codes. cleanit compares the base language only (`get_language_groups` in
  `cleanit/utils.py`). A `pt` rule applies to a `pt-BR` file. A rule without `languages` applies to all
  languages.

## How to write a safe pattern

Correct real dialogue is more important than fixing more OCR errors.

- **Do not use a bare `\s` to close a gap in one word.** `\s` also matches the `"\n"` between two lines
  of the entry. The rule then joins two lines or two words. `fix-broken-c-cedilla[ocr:pt]` had this bug.
  Its regression case is `tests/data/cases/ocr-pt-c-cedilla-no-line-merge-pt-br/`. Use a space
  character, or a character class without `\n`.
- **Use a list of words, not a broad character class.** See `fix-l-to-i-words[ocr:pt]` and
  `replace-0-to-o-common-words[ocr:en]`. Broad patterns changed real names (`TiVo`, `DeVille`, from "a
  capital V between two lowercase letters") and real text (`O2`, from "an O before digits").
- Add `examples:` for the text that the rule must change, and for the text that it must not change. Each
  example is a test. See `docs/testing.md`.
- Before you merge a broad change, check it against real subtitles. See `docs/rule-validation.md`.

## Try a rule

```bash
uv run cleanit -t default --test --debug some.srt
```

`--test` does not save the file. `--debug` logs each rule that matched, with the text before and after.
