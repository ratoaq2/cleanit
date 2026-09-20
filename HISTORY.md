# Changelog

## 0.5.1

**Release date:** 2026-09-20

- Add `--version` option to the CLI
- Stop release tags like DTS, AAC, SDR, and SDH from being detected as languages
- Switch lint hook to pre-commit

## 0.5.0

**Release date:** 2026-09-18

- Modernize packaging, linting, and CI tooling
- Fix OCR rules that wrongly matched real words, plurals, and names
- Remove pt-BR sync credits, upload credits, and anti-piracy notices from subtitles
- Drop orphan dash-only lines left behind by SDH removal

## 0.4.9

**Release date:** 2025-07-26

- Update dependencies and supported python versions

## 0.4.8

**Release date:** 2024-06-23

- Drop python 3.8 support
- Add python 3.12 support
- Add support to arm docker images
- Added new no-spam pt rules

## 0.4.7

**Release date:** 2023-02-12

- Add new `ocr` and `no-spam` rules

## 0.4.6

**Release date:** 2023-01-09

- Add more spam rules for Portuguese language

## 0.4.5

**Release date:** 2022-12-31

- Add option to filter out old subtitles

## 0.4.4

**Release date:** 2021-04-07

- Properly handle PermissionError when searching for default configurations

## 0.4.3

**Release date:** 2021-04-07

- Better error handling
- Updated out-of-box rules

## 0.4.2

**Release date:** 2021-03-20

- Fixes default configuration loading

## 0.4.1

**Release date:** 2021-03-16

- Fixes missing default configuration files

## 0.4.0

**Release date:** 2021-03-16

- Major refactoring
- Drop python 2 support
- Added support for languages and tags
- Added default rules

## 0.3.0

**Release date:** 2021-03-02

- Python 3.x support

## 0.2.1

**Release date:** 2016-02-28

- Adding guess encoding back without python-magic dependency

## 0.2

**Release date:** 2016-02-27

- Removing chardet and python-magic dependencies. Either encoding is
  specified or it should be guessed by pysrt

## 0.1

**Release date:** 2015-10-16

- Initial release
