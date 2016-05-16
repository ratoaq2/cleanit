# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


def clean(value, rules, replacement=None):
    """Cleans the value using the specified rules

    :param value: the string value to be cleaned
    :type value: str
    :param rules: the clean rules to be used
    :type rules: list of cleanit.rule.Rule
    :param replacement: the replacement string
    :type replacement: str
    :return: the cleaned value after applying all the rules
    :rtype: str
    """
    result = value
    for rule in rules:
        previous = result
        result = rule.apply(previous, replacement=replacement)
        if not result:
            if rule.whitelist:
                logger.debug('Match found: <%s> in whitelist. Keeping:\n%s', rule, previous)
                result = previous
            else:
                logger.debug('Match found: <%s>. Removing:\n%s', rule, previous)
            break
        elif result != previous:
            logger.debug("Match found: <%s>.\nChanging item:\n\t%s\nto\n\t%s\n", rule, previous, result)

    return result
