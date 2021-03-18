# -*- coding: utf-8 -*-
import os

from babelfish import Language
from pysrt import SubRipFile, SubRipItem

from cleanit.config import Config

here = os.path.abspath(os.path.dirname(__file__))
enabled = False


def regenerate(config: Config, index: int, language: Language):
    input_srt = SubRipFile()
    expected_srt = SubRipFile()
    for rule in config.rules:
        for text, expected in rule.examples.items():
            if rule.matches(language):
                start = len(input_srt)
                end = start + 1
                input_srt.append(SubRipItem(start=start, end=end, text=text))
                if expected:
                    expected_srt.append(SubRipItem(start=start, end=end, text=expected))

    input_srt.clean_indexes()
    expected_srt.clean_indexes()
    if enabled:
        input_srt.save(os.path.join(here, 'data', f'{index:04d}.{str(language)}.srt'))
        expected_srt.save(os.path.join(here, 'data', f'{index:04d}-expected.{str(language)}.srt'))


def main():
    config = Config()
    languages = [Language.fromietf(lang) for lang in ('en', 'pt-BR')]
    i = 0
    for language in languages:
        regenerate(config, i, language)
        i += 1


if __name__ == '__main__':
    main()
