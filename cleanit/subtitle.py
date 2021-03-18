# -*- coding: utf-8 -*-
import logging
import os
from io import StringIO
from typing import Optional, Set

import chardet
import pysrt
from babelfish import language_converters, country_converters, Language, LanguageReverseConverter, LanguageReverseError
from pysrt import SubRipFile

from .rule import Rules, Change, Changes

logger = logging.getLogger(__name__)


class CleanitLanguageConverter(LanguageReverseConverter):
    @property
    def codes(self):
        return (language_converters['alpha3b'].codes |
                language_converters['alpha2'].codes |
                language_converters['name'].codes |
                language_converters['opensubtitles'].codes |
                country_converters['name'].codes)

    def convert(self, alpha3: str, country: str = None, script: str = None):
        return str(Language(alpha3, country, script))

    def reverse(self, name: str):
        name = name.lower()
        for conv in [Language.fromietf,
                     Language,
                     Language.fromalpha3b,
                     Language.fromalpha2,
                     Language.fromname,
                     Language.fromopensubtitles]:
            try:
                reverse = conv(name)
                return reverse.alpha3, reverse.country, reverse.script
            except (ValueError, LanguageReverseError):
                pass

        return 'und', None, None


language_converters['cleanit'] = CleanitLanguageConverter()


def get_subtitle_language(path: str):
    lang = os.path.splitext(os.path.splitext(path)[0])[1] or '.und'
    return Language.fromcleanit(lang[1:])


class Subtitle:
    def __init__(self, path: str, encoding: str = None):
        self.path = path
        self.language = get_subtitle_language(path)
        self.encoding = encoding
        self.subtitle: Optional[SubRipFile] = None

    def __repr__(self):
        return f'<{self.__class__.__name__} [{self.path}]>'

    @property
    def content(self):
        if self.subtitle:
            writer = StringIO()
            self.subtitle.write_into(writer)
            writer.seek(0)
            return writer.read().strip()

    @property
    def name(self):
        return os.path.split(self.path)[1]

    def match(self, languages: Set[Language]):
        return not languages or self.language in languages

    def save(self, path: str = None, encoding: str = None):
        self.subtitle.save(path=path or self.path, encoding=encoding or self.encoding)

    def guess_encoding(self):
        with open(self.path, 'rb') as f:
            content = f.read()

        # always try utf-8 first
        encodings = ['utf-8']

        # add language-specific encodings
        if self.language.alpha3 == 'zho':
            encodings.extend(['gb18030', 'big5'])
        elif self.language.alpha3 == 'jpn':
            encodings.append('shift-jis')
        elif self.language.alpha3 == 'ara':
            encodings.append('windows-1256')
        elif self.language.alpha3 == 'heb':
            encodings.append('windows-1255')
        elif self.language.alpha3 == 'tur':
            encodings.extend(['iso-8859-9', 'windows-1254'])
        elif self.language.alpha3 == 'pol':
            # Eastern European Group 1
            encodings.extend(['windows-1250'])
        elif self.language.alpha3 == 'bul':
            # Eastern European Group 2
            encodings.extend(['windows-1251'])
        else:
            # Western European (windows-1252)
            encodings.append('latin-1')

        # try to decode
        for encoding in encodings:
            try:
                content.decode(encoding)
            except UnicodeDecodeError:
                pass
            else:
                return encoding

        logger.warning('Could not guess encoding from language')

        # fallback on chardet
        encoding = chardet.detect(content)['encoding']
        logger.info(f'Chardet found encoding {encoding}')

        return encoding

    def clean(self, rules: Rules, clean_indexes=True):
        rules = Rules(rules=rules, tags=rules.tags, languages={self.language})
        self.encoding = self.encoding or self.guess_encoding()
        self.subtitle = pysrt.open(self.path, encoding=self.encoding)
        track_changes = logger.isEnabledFor(logging.DEBUG)
        changes = Changes(self.subtitle) if track_changes else None

        modified = False
        for i, item in reversed(list(enumerate(self.subtitle))):
            change = Change(item) if track_changes else None
            text, changed = rules.apply(item.text, change=change)
            if changed:
                modified = True
                if not text:
                    del self.subtitle[i]
                else:
                    item.text = text
                if track_changes:
                    changes.append(change)

        if modified:
            if track_changes:
                max_chars = max([c.max_chars for c in changes])
                for c in changes:
                    c.max_chars = max_chars

                logger.debug(f'Changes for {changes}')
            if clean_indexes:
                self.subtitle.clean_indexes()

        return modified

    def finalize(self):
        self.subtitle = None
