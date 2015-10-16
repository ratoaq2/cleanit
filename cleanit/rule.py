# -*- coding: utf-8 -*-
import logging
import re


logger = logging.getLogger(__name__)


class Rule(object):
    def __init__(self, regex, replacement, flags, whitelist):
        self.regex = regex
        self.replacement = replacement
        self.flags = flags
        self.whitelist = whitelist

    def __repr__(self):
        return '<%s [%s, %s, %s, %s]>' % (
            self.__class__.__name__, self.regex.pattern, self.flags, self.replacement, self.whitelist)

    def apply(self, text):
        m = self.regex.search(text)
        if not m:
            return text

        if self.replacement:
            return self.regex.sub(self.replacement, text)

        return None

    @staticmethod
    def from_config(config):
        flags = 0
        for flag in [f.upper() for f in config.get('flags', [])]:
            logger.debug("Configuring flag '%s'" % flag)
            flags |= re.__dict__.get(flag)

        rtype = config.get('type', 'text')
        mtype = config.get('match', 'contains')
        pattern = (lambda t: t if rtype == 'regex' else re.escape(t))(config.get('pattern'))

        if mtype in {'endswith', 'exact'}:
            pattern += '$'
        if mtype in {'startswith', 'exact'}:
            pattern = '^' + pattern

        regex = re.compile(pattern, flags)
        rule = Rule(regex, config.get('replacement'), config.get('flags'), config.get('whitelist'))
        logger.debug("Created %s" % rule)
        return rule
