# CleanIt

Subtitles extremely clean.

[![Latest
Version](https://img.shields.io/pypi/v/cleanit.svg)](https://pypi.python.org/pypi/cleanit)

[![tests](https://github.com/ratoaq2/cleanit/actions/workflows/test.yml/badge.svg)](https://github.com/ratoaq2/cleanit/actions/workflows/test.yml)

[![License](https://img.shields.io/github/license/ratoaq2/cleanit.svg)](https://github.com/ratoaq2/cleanit/blob/master/LICENSE)

  - Project page  
    <https://github.com/ratoaq2/cleanit>

**CleanIt** is a command line tool that helps you to keep your subtitles
clean. You can specify your own rules to detect entries to be removed or
patterns to be replaced. Simple text matching or complex regex can be
used. It comes with standard rules out of the box:

  - ocr: Fix common OCR errors
  - tidy: Fix common formatting issues (e.g.: extra/missing spaces after
    punctuation)
  - no-sdh: Remove SDH descriptions
  - no-lyrics: Remove lyrics
  - no-spam: Remove ads and spams
  - no-style: Remove font style tags like \<i\> and \<b\>
  - minimal: includes only ocr and tidy rules
  - default: includes all rules except no-style

## Usage

### CLI

Clean subtitles:

    $ cat mysubtitle.srt
    1
    00:00:46,464 --> 00:00:48,549
    -And then what?
    -| don't know.
    
    2
    00:49:07,278 --> 00:49:09,363
    - If you cross the sea
    with an army you bought ...
    
    
    $ cleanit -t default mysubtitle.en.srt
    1 subtitle collected / 0 subtitle filtered out / 0 path ignored
    1 subtitle saved / 0 subtitle unchanged
    
    $ cat mysubtitle.srt
    1
    00:00:46,464 --> 00:00:48,549
    - And then what?
    - I don't know.
    
    2
    00:49:07,278 --> 00:49:09,363
    If you cross the sea
    with an army you bought...
    
    
    $ cleanit -t ocr -t no-sdh -t tidy -l en -l pt-BR ~/subtitles/
    423 subtitles collected / 107 subtitles filtered out / 0 path ignored
    Cleaning subtitles  [####################################]  100%
    268 subtitles saved / 155 subtitles unchanged

Using docker:

    $ docker run -it --rm -v /medias:/medias -u $(id -u username):$(id -g username) ratoaq2/cleanit -t default /medias
    1072 subtitles collected / 0 subtitle filtered out / 0 path ignored
    Cleaning subtitles  [####################################]  100%
    980 subtitle saved / 92 subtitles unchanged

### API

``` python
from cleanit import Config, Subtitle

sub = Subtitle('/subtitle/path/subtitle.en.srt')
cfg = Config.from_path('/config/path')
rules = cfg.select_rules(tags={'ocr'})
if sub.clean(rules):
    sub.save()
```

### YAML Configuration file

``` yaml
templates:
  - &ocr
    tags:
      - ocr
      - minimal
      - default
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
