# -*- coding: utf-8 -*-
import logging

import chardet
import pysrt

from .core import clean

logger = logging.getLogger(__name__)


class Subtitle(object):
    def __init__(self, path, encoding=None):
        self.path = path
        self.encoding = encoding if encoding else self.guess_encoding(path)
        self.subtitle = None

    def __repr__(self):
        return '<%s [%s]>' % (self.__class__.__name__, self.path)

    def load(self):
        self.subtitle = pysrt.open(self.path, encoding=self.encoding)

    def save(self, path=None, encoding=None):
        self.subtitle.save(path=path if path else self.path, encoding=encoding if encoding else self.encoding)

    def guess_encoding(self, path):
        # always try utf-8 first
        encodings = ['utf-8', 'latin-1', 'windows-1251', 'windows-1250', 'iso-8859-9', 'windows-1254', 'windows-1255',
                     'windows-1256', 'shift-jis', 'gb18030', 'big5']

        # try to decode
        logger.debug('Trying encodings %r', encodings)

        with open(path, 'r') as f:
            content = f.read()
            for encoding in encodings:
                try:
                    content.decode(encoding)
                except UnicodeDecodeError:
                    pass
                else:
                    logger.info('Guessed encoding %s', encoding)
                    return encoding

            logger.warning('Could not guess encoding from language')

            # fallback on chardet
            encoding = chardet.detect(content)['encoding']
            logger.info('Chardet found encoding %s', encoding)

        return encoding

    def clean(self, rules, clean_indexes=True):
        self.load()

        modified = False
        for i, item in reversed(list(enumerate(self.subtitle))):
            modified_text = clean(item.text, rules)
            if modified_text != item.text:
                modified = True
                if modified_text is None:
                    del self.subtitle[i]
                    break
                else:
                    item.text = modified_text

        if modified and clean_indexes:
            self.subtitle.clean_indexes()

        return modified
