# CleanIt

Subtitles extremely clean.

[![Latest Version](https://img.shields.io/pypi/v/cleanit.svg)](https://pypi.python.org/pypi/cleanit)
[![Supported versions](https://img.shields.io/pypi/pyversions/cleanit.svg)](https://pypi.python.org/pypi/cleanit)
[![tests](https://github.com/ratoaq2/cleanit/actions/workflows/test.yml/badge.svg)](https://github.com/ratoaq2/cleanit/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/ratoaq2/cleanit.svg)](https://github.com/ratoaq2/cleanit/blob/main/LICENSE)

CleanIt fixes OCR errors and removes clutter from `.srt` subtitle files.

| Before | After |
| --- | --- |
| `-And then what?`<br>`-\| don't know.` | `- And then what?`<br>`- I don't know.` |
| `- If you cross the sea`<br>`with an army you bought ...` | `If you cross the sea`<br>`with an army you bought...` |
| `[DOOR SLAMS]` | *(entry removed)* |

## Quick start

You need [uv](https://docs.astral.sh/uv/). First, see what CleanIt will change. `--test` does not change
the file:

```console
$ uvx cleanit -t default --test --debug movie.en.srt
```

Then clean the file:

```console
$ uvx cleanit -t default movie.en.srt
1 subtitle collected / 0 subtitle filtered out / 0 path ignored
1 subtitle saved / 0 subtitle unchanged
```

> [!WARNING]
> CleanIt writes the result into the same file. It does not make a backup. Use `--test` first, or keep a
> copy of your files.

## What it cleans

Select the rules with one or more `-t` tags:

| Tag | What it does | Example |
| --- | --- | --- |
| `ocr` | Fixes common OCR errors. | `And if l refuse?` → `And if I refuse?` |
| `tidy` | Fixes spaces, dashes, and punctuation. | `you bought ...` → `you bought...` |
| `no-sdh` | Removes SDH descriptions (sounds and speaker names for deaf and hard-of-hearing viewers). | `[DOOR SLAMS]` → removed |
| `no-lyrics` | Removes song lyrics. | `♪ Those icy fingers ♪` → removed |
| `no-spam` | Removes ads and credits. | `Subtitles by FooBar` → removed |
| `no-style` | Removes font style tags. | `<i>Where are you?</i>` → `Where are you?` |

Two tags select a group of rules:

- `minimal`: `ocr` and `tidy`.
- `default`: all rules except `no-style`.

## Languages

CleanIt reads the language from the file name: `movie.en.srt` is English, and `movie.pt-BR.srt` is
Brazilian Portuguese.

- All files get the rules for all languages.
- English and Portuguese files also get their own OCR, tidy, and spam rules. German files also get their
  own spam rules. A `pt` rule also applies to `pt-BR` files.
- A file without a language code in its name (`movie.srt`) gets only the rules for all languages.

CleanIt reads only `.srt` files.

## Installation

Run it without installing it:

```console
$ uvx cleanit --help
```

Install it as a command (this adds `cleanit` to your `PATH`):

```console
$ uv tool install cleanit
```

Or install it with [pip](https://pip.pypa.io):

```console
$ pip install cleanit
```

## Usage

Clean one file, many files, or all `.srt` files in a folder and its subfolders:

```console
$ cleanit -t default movie.en.srt
$ cleanit -t ocr -t no-sdh -t tidy -l en -l pt-BR ~/subtitles/
423 subtitles collected / 107 subtitles filtered out / 0 path ignored
Cleaning subtitles  [####################################]  100%
268 subtitles saved / 155 subtitles unchanged
```

Clean only the files that changed in the last 2 days:

```console
$ cleanit -t default -a 2d ~/subtitles/
```

| Option | What it does |
| --- | --- |
| `-t`, `--tag` | Rule tag to use. Required. Use it more than one time for more tags. |
| `-l`, `--language` | Clean only the files in this language (IETF code, for example `en` or `pt-BR`). Use it more than one time for more languages. |
| `-a`, `--age` | Clean only the files that changed in this time, for example `12h` or `1w2d`. |
| `-c`, `--config` | Use your own rule file. See [Custom rules](#custom-rules). |
| `-e`, `--encoding` | Save the files with this encoding, for example `utf-8`. |
| `-f`, `--force` | Save the file also when no rule changed it. |
| `--test` | Do not change any file. Use it with `--debug`. |
| `--debug` | Show each change: the rule name, and the text before and after. |
| `-v`, `--verbose` | Show more messages. |
| `--version` | Show the version. |

## Custom rules

You can add rules, or turn off a built-in rule. Write a YAML file:

```yaml
rules:
  # Turn off a built-in rule. Use --debug to see the rule names.
  replace-ellipsis-character[ocr]:
    disabled: true

  # Add a new rule.
  replace-gonna[custom:en]:
    tags: default
    languages: en
    patterns: '\bgonna\b'
    replacement: 'going to'
```

Use the file with `-c`:

```console
$ cleanit -t default -c my-rules.yml movie.en.srt
```

Or put the file in your configuration folder. CleanIt then uses it each time. The file name must start
with `cleanit` and end with `.yml`, `.yaml`, or `.json`, for example `cleanit-custom.yml`.

| System | Folder |
| --- | --- |
| Linux | `~/.config/cleanit/` |
| macOS | `~/Library/Application Support/cleanit/` |
| Windows | `%LOCALAPPDATA%\Rato\cleanit\` |

A rule without `replacement` removes the full subtitle entry when it matches. For all rule fields, and for
tips to write safe patterns, see
[docs/rules.md](https://github.com/ratoaq2/cleanit/blob/main/docs/rules.md).

## Docker

CleanIt is also available as a [Docker image](https://hub.docker.com/r/ratoaq2/cleanit):

```console
$ docker run -it --rm -v /medias:/medias -u $(id -u username):$(id -g username) ratoaq2/cleanit -t default /medias
1072 subtitles collected / 0 subtitle filtered out / 0 path ignored
Cleaning subtitles  [####################################]  100%
980 subtitle saved / 92 subtitles unchanged
```

## Python API

```python
from cleanit import Config, Subtitle

sub = Subtitle("/subtitle/path/subtitle.en.srt")
cfg = Config.from_path("/config/path")
rules = cfg.select_rules(tags={"ocr"})
if sub.clean(rules):
    sub.save()
```

## Contributing

Bug reports and pull requests are welcome.

- To report a bug, [open an issue](https://github.com/ratoaq2/cleanit/issues). Add the command, the
  language, and the text of the subtitle entry before and after.
- To change the code or the rules, read
  [CONTRIBUTING.md](https://github.com/ratoaq2/cleanit/blob/main/CONTRIBUTING.md).
- The changes of each version are in
  [HISTORY.md](https://github.com/ratoaq2/cleanit/blob/main/HISTORY.md).

## License

[Apache License 2.0](https://github.com/ratoaq2/cleanit/blob/main/LICENSE).
