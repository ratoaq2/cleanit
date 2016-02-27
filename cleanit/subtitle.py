# -*- coding: utf-8 -*-
import logging
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
        self.subtitle = pysrt.open(self.path, encoding=self.encoding)

    def save(self, path=None, encoding=None):
        self.subtitle.save(path=path if path else self.path, encoding=encoding if encoding else self.encoding)

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
