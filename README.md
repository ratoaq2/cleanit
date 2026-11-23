<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ratoaq2/cleanit/main/docs/images/logo-dark.png">
    <img alt="cleanit: Clean your subtitles" src="https://raw.githubusercontent.com/ratoaq2/cleanit/main/docs/images/logo-light.png" width="400">
  </picture>
</h1>

cleanit fixes OCR errors and removes clutter from your `.srt` subtitle files.

[![PyPI version](https://img.shields.io/pypi/v/cleanit.svg)](https://pypi.org/project/cleanit/)
[![Python versions](https://img.shields.io/pypi/pyversions/cleanit.svg)](https://pypi.org/project/cleanit/)
[![Tests](https://github.com/ratoaq2/cleanit/actions/workflows/test.yml/badge.svg)](https://github.com/ratoaq2/cleanit/actions/workflows/test.yml)
[![Docker pulls](https://img.shields.io/docker/pulls/ratoaq2/cleanit.svg)](https://hub.docker.com/r/ratoaq2/cleanit)
[![License](https://img.shields.io/github/license/ratoaq2/cleanit.svg)](https://github.com/ratoaq2/cleanit/blob/main/LICENSE)

![cleanit cleans a subtitle file: before and after](https://raw.githubusercontent.com/ratoaq2/cleanit/main/docs/images/demo.gif)

## Why cleanit

OCR tools make text subtitles from image subtitles. The text often has errors, for example `l` in place of
`I`. Many subtitles also have text that you do not want: sound descriptions, song lyrics, ads, and style
tags.

cleanit finds these problems with a set of rules, and fixes them:

| Before | After |
| --- | --- |
| `-And then what?`<br>`-\| don't know.` | `- And then what?`<br>`- I don't know.` |
| `- If you cross the sea`<br>`with an army you bought ...` | `If you cross the sea`<br>`with an army you bought...` |
| `[DOOR SLAMS]` | *(entry removed)* |

[pgsrip](https://github.com/ratoaq2/pgsrip) uses cleanit to clean the subtitles after the OCR.

## Quick start

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. See what cleanit will change. `--test` does not change the file:

   ```console
   $ uvx cleanit -t default --test --debug movie.en.srt
   ```

3. Clean the file:

   ```console
   $ uvx cleanit -t default movie.en.srt
   Collecting subtitles  [####################################]  100%
   1 subtitle collected / 0 subtitle filtered out / 0 path ignored
   Cleaning subtitles  [####################################]  100%
   1 subtitle saved / 0 subtitle unchanged
   ```

> [!WARNING]
> cleanit writes the result into the same file. It does not make a backup. Use `--test` first, or keep a
> copy of your files.

## Installation

Use one of these commands:

| Command | When to use it |
| --- | --- |
| `uvx cleanit` | You want to use cleanit without installing it. |
| `uv tool install cleanit` | Recommended. This adds `cleanit` to your `PATH`. |
| `pip install cleanit` | You want to use cleanit as a Python library. |

To upgrade, use `uv tool upgrade cleanit`.

### Docker

cleanit is also available as a [Docker image](https://hub.docker.com/r/ratoaq2/cleanit):

```console
$ docker run -it --rm -v /medias:/medias -u $(id -u):$(id -g) ratoaq2/cleanit -t default /medias
1072 subtitles collected / 0 subtitle filtered out / 0 path ignored
Cleaning subtitles  [####################################]  100%
980 subtitles saved / 92 subtitles unchanged
```

## Usage

Clean one file:

```console
$ cleanit -t default movie.en.srt
```

Clean all `.srt` files in a folder and its subfolders:

```console
$ cleanit -t default ~/subtitles/
423 subtitles collected / 0 subtitle filtered out / 0 path ignored
Cleaning subtitles  [####################################]  100%
268 subtitles saved / 155 subtitles unchanged
```

Clean only the English and the Brazilian Portuguese files:

```console
$ cleanit -t default -l en -l pt-BR ~/subtitles/
```

Clean only the files that changed in the last 2 days:

```console
$ cleanit -t default -a 2d ~/subtitles/
```

Fix only the OCR errors, spaces, and punctuation. Keep all entries:

```console
$ cleanit -t minimal movie.en.srt
```

Also remove the style tags, for example `<i>`:

```console
$ cleanit -t default -t no-style movie.en.srt
```

See each change, with the rule name, and the text before and after:

```console
$ cleanit -t default --debug movie.en.srt
```

### Rule tags

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

### Languages

cleanit reads the language from the file name: `movie.en.srt` is English, and `movie.pt-BR.srt` is
Brazilian Portuguese.

- All files get the rules for all languages.
- English and Portuguese files also get their own OCR, tidy, and spam rules. German files also get their
  own spam rules. A `pt` rule also applies to `pt-BR` files.
- A file without a language code in its name (`movie.srt`) gets only the rules for all languages.

### Main options

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

Run `cleanit --help` for all options.

### Custom rules

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

Or put the file in your configuration folder. cleanit then uses it each time. The file name must start
with `cleanit` and end with `.yml`, `.yaml`, or `.json`, for example `cleanit-custom.yml`.

| System | Folder |
| --- | --- |
| Linux | `~/.config/cleanit/` |
| macOS | `~/Library/Application Support/cleanit/` |
| Windows | `%LOCALAPPDATA%\Rato\cleanit\` |

A rule without `replacement` removes the full subtitle entry when it matches. For all rule fields, and for
tips to write safe patterns, see
[docs/rules.md](https://github.com/ratoaq2/cleanit/blob/main/docs/rules.md).

### Python API

You can also use cleanit in your Python code. See
[docs/python-api.md](https://github.com/ratoaq2/cleanit/blob/main/docs/python-api.md).

## FAQ

**Does cleanit make a backup?**

No. cleanit writes the result into the same file. Use `--test --debug` first to see the changes.

**Why did cleanit remove a full subtitle entry?**

A rule without `replacement` removes the entry when it matches. Use `--debug` to see the rule name. To keep
these entries, turn off the rule in a [custom rule file](#custom-rules).

**How do I turn off one rule?**

Add the rule name with `disabled: true` to a [custom rule file](#custom-rules).

**Which file formats does cleanit read?**

Only `.srt`.

**Why does my file get only some of the rules?**

cleanit reads the language from the file name. A file without a language code in its name gets only the
rules for all languages. See [Languages](#languages).

**Can I add rules for my language?**

Yes. Write them in a [custom rule file](#custom-rules). To add them to cleanit for all users, read
[CONTRIBUTING.md](https://github.com/ratoaq2/cleanit/blob/main/CONTRIBUTING.md).

## Report a bug

[Open an issue](https://github.com/ratoaq2/cleanit/issues). Add:

- The command that you used.
- The language of the subtitle file.
- The text of the subtitle entry before and after. Run your command with `--test --debug` and copy the
  output.

## Contributing

Pull requests are welcome. To change the code or the rules, read
[CONTRIBUTING.md](https://github.com/ratoaq2/cleanit/blob/main/CONTRIBUTING.md). The changes of each
version are in [HISTORY.md](https://github.com/ratoaq2/cleanit/blob/main/HISTORY.md).

## License

[Apache License 2.0](https://github.com/ratoaq2/cleanit/blob/main/LICENSE).

The cleanit name, logo, and icon are not covered by the Apache License 2.0. All rights reserved.
