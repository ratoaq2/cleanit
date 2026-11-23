# Python API

You can use cleanit in your Python code. This example cleans one file with the `default` rules:

```python
from cleanit import Config, Subtitle

sub = Subtitle("movie.en.srt")
cfg = Config.from_path()
rules = cfg.select_rules(tags={"default"})
if sub.clean(rules):
    sub.save()
```

- `Subtitle(path)` reads the language from the file name, as the command does.
- `Config.from_path()` loads the built-in rules and the rule files in your configuration folder. To add
  your own rule file, give its path: `Config.from_path("my-rules.yml")`. You can also give a folder. Then
  cleanit loads the rule files in it with a name such as `cleanit-custom.yml`.
- `Config.select_rules(tags=...)` selects the rules with these tags. The tags are the same as for `-t`.
- `Subtitle.clean(rules)` applies the rules for the language of the file. It returns `True` when a rule
  changed the text.
- `Subtitle.save()` writes the result into the same file. It does not make a backup. To write to another
  file, give its path: `sub.save("clean.en.srt")`.
