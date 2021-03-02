# -*- coding: utf-8 -*-

from . import core


def clean(value, rules):
    """Cleans the value using specified rules

    :param value: the string value to be cleaned
    :type value: str
    :param rules: the clean rules to be used
    :type rules: list of cleanit.rule.Rule
    :return: the cleaned value after applying all the rules
    :rtype: str
    """
    return core.clean(value, rules, replacement='')


def clean_subtitle(subtitle, rules):
    """Cleans the subtitle using the rules passed as parameter

    :param subtitle: the subtitle to be cleaned
    :type subtitle: cleanit.subtitle.Subtitle
    :param rules: the clean rules to be used
    :type rules: list of cleanit.rule.Rule
    :return: True if the subtitle was modified
    :rtype: bool
    """
    return subtitle.clean(rules)


def save_subtitle(subtitle, path=None, encoding=None):
    """Saves the specified subtitle

    :param subtitle: the subtitle to be saved
    :type subtitle: cleanit.subtitle.Subtitle
    :param path: the path to be used or None to use the subtitle's path
    :type path: str
    :param encoding: the encoding to be used or None to use subtitle's encoding
    :type encoding: str
    """
    subtitle.save(path=path, encoding=encoding)
