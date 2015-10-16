# -*- coding: utf-8 -*-
import chardet
import logging
import magic
import pysrt


logger = logging.getLogger(__name__)


class Subtitle(object):

    def __init__(self, path, encoding=None):
        self.path = path
        self.encoding = encoding
        self.subtitle = None

    def __repr__(self):
        return '<%s [%s]>' % (self.__class__.__name__, self.path)

    def load(self):
        if not self.encoding:
            self.encoding = self.guess_encoding()
        self.subtitle = pysrt.open(self.path, encoding=self.encoding)

    def save(self, path=None, encoding=None):
        self.subtitle.save(path=path if path else self.path, encoding=encoding if encoding else self.encoding)

    def guess_encoding(self):
        filename = self.path.decode('utf-8')

        # Unfortunately there are several magic modules...
        encoding = None

        # Debian/Ubuntu python-magic
        if hasattr(magic.Magic, 'file'):
            m = magic.open(magic.MAGIC_MIME_ENCODING)
            m.load()
            encoding = m.file(filename)
            logger.debug("Guessed encoding '%s' for '%s' using debian's python-magic" % (encoding, self.path))
            m.close()

        # https://pypi.python.org/pypi/python-magic
        elif hasattr(magic.Magic, 'from_file'):
            m = magic.Magic(mime_encoding=True)
            encoding = m.from_file(filename)
            logger.debug("Guessed encoding '%s' for '%s' using pypi's python-magic" % (encoding, self.path))

        # https://pypi.python.org/pypi/filemagic
        elif hasattr(magic.Magic, 'id_filename'):
            with magic.Magic(flags=magic.MAGIC_MIME_ENCODING) as m:
                encoding = m.id_filename(filename)
            logger.debug("Guessed encoding '%s' for '%s' using pypi's filemagic" % (encoding, self.path))

        if not encoding or encoding in ['unknown-8bit']:
            with open(filename, 'rb') as f:
                encoding = chardet.detect(f.read())['encoding']
            logger.debug("Guessed encoding '%s' for '%s' using chardet" % (encoding, self.path))

        return encoding

    def clean(self, rules, clean_indexes=True):
        self.load()

        modified = False
        for i, item in reversed(list(enumerate(self.subtitle))):
            for rule in rules:
                modified_text = rule.apply(item.text)
                if not modified_text:
                    if not rule.whitelist:
                        logger.debug("Match found: '%s'. Removing item:\n%s" % (rule, item))
                        del self.subtitle[i]
                        modified = True
                    else:
                        logger.debug("Match found: '%s' in whitelist. Keeping item:\n%s" % (rule, item))
                    break
                elif modified_text != item.text:
                    logger.debug("Match found: '%s'. Changing item:\n%s\nto\n\n%s\n" % (rule, item, modified_text))
                    item.text = modified_text
                    modified = True

        if modified and clean_indexes:
            self.subtitle.clean_indexes()

        return modified
