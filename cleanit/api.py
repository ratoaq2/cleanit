# -*- coding: utf-8 -*-


def clean_subtitle(subtitle, rules):
    return subtitle.clean(rules)


def save_subtitle(subtitle, path=None, encoding=None):
    subtitle.save(path=path, encoding=encoding)
