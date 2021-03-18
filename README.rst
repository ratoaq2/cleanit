CleanIt
==========
Subtitles extremely clean.

.. image:: https://img.shields.io/pypi/v/cleanit.svg
    :target: https://pypi.python.org/pypi/cleanit
    :alt: Latest Version

.. image:: https://travis-ci.org/ratoaq2/cleanit.svg?branch=master
   :target: https://travis-ci.org/ratoaq2/cleanit
   :alt: Travis CI build status

.. image:: https://img.shields.io/github/license/ratoaq2/cleanit.svg
   :target: https://github.com/ratoaq2/cleanit/blob/master/LICENSE
   :alt: License

:Project page: https://github.com/ratoaq2/cleanit

**CleanIt** is a command line tool (written in python) that helps you to keep your subtitles clean.
You can specify your own rules to detect entries to be removed or patterns to be replaced.
Simple text matching or complex regex can be used.
It comes with standard rules out of the box:

* ocr: Fix common OCR errors
* tidy: Fix common formatting issues (e.g.: extra/missing spaces after punctuation)
* no-sdh: Remove SDH descriptions
* no-lyrics: Remove lyrics
* no-spam: Remove ads and spams
* no-style: Remove font style tags like <i> and <b>
* minimal: includes only ocr and tidy rules
* default: includes all rules except no-style

Usage
-----
CLI
^^^
Clean subtitles::

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


API
^^^
.. code:: python

    from cleanit import Config, Subtitle

    sub = Subtitle('/subtitle/path/subtitle.en.srt')
    cfg = Config.from_path('/config/path')
    rules = cfg.select_rules(tags={'ocr'})
    if sub.clean(rules):
        sub.save()


YAML Configuration file
^^^^^^^^^^^^^^^^^^^^^^^

.. code:: yaml
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
