# Architecture

cleanit has two parts:

- A generic rule engine in Python. It loads rules, selects them by tag and language, and applies them.
- The rule data in YAML, in `cleanit/data/`. All the cleaning behavior (OCR fixes, tidy, SDH, lyrics,
  spam, and style removal) is in this data. See `docs/rules.md`.

To add or fix a cleaning behavior, change the YAML. Change the Python engine only when the engine itself
is wrong or needs a new capability.

## Modules

| Module | Role |
| --- | --- |
| `cleanit/__init__.py` | Package metadata. Exports `Config` and `Subtitle`. |
| `cleanit/cli.py` | The `cleanit` command (click). Finds `.srt` files, filters them by language (`-l`) and age (`-a`), selects the rules by tag (`-t`), then cleans and saves each file. `--test` does not save. |
| `cleanit/config.py` | Loads the built-in rules, the user configuration files, and a `-c` file. Merges them, sorts the rules by priority, and selects them (`Config.select_rules`). |
| `cleanit/rule.py` | `Rule` and `Rules`: compile the patterns and apply them to a text. `Change` and `Changes` record each match for the debug log. |
| `cleanit/subtitle.py` | `Subtitle`: reads an `.srt` file (the encoding comes from `chardet`), finds the language in the file name, cleans each entry, and saves the file. |
| `cleanit/schema.py` | JSON Schema of a rule file. |
| `cleanit/utils.py` | Loads and validates the rule files, merges them, and finds the language groups. |
| `cleanit/data/__init__.py` | `default_config_resources`: the list of built-in rule files. |
| `cleanit/data/*.yml` | The built-in rules. See `docs/rules.md`. |

## Public API

Other packages use this API. pgsrip calls it for each subtitle text. Keep it stable. A change to it is a
breaking change and needs a line in `HISTORY.md`.

```python
from cleanit import Config, Subtitle

rules = Config.from_path(path).select_rules(tags={"ocr"}, languages={language})
text = rules.apply(text, "")[0]  # a plain string in, a string or None out

sub = Subtitle("/path/subtitle.en.srt")
if sub.clean(rules):
    sub.save()
```

## Debug cost

`Subtitle.clean` builds `Change` objects only when the `cleanit` logger has the debug level (`--debug`
or `-v`). Without debug, cleanit does not record the matches. Keep this check when you change the
cleaning loop.
