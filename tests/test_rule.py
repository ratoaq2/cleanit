# -*- coding: utf-8 -*-

from cleanit.rule import Rule


def test_text_exact():
    pattern = """Lorem ipsum dolor sit amet,
ius ex maiorum disputationi"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'exact'}

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert actual is None


def test_text_exact_replacement():
    pattern = """Lorem ipsum dolor sit amet,
ius ex maiorum disputationi"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = 'a b c'
    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'exact', 'replacement': replacement}
    expected = replacement

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_text_exact_no_match():
    pattern = """Lorem ipsum dolor sit amet,
ius ex maiorum disputationi"""
    text = """Lorem ipsum dolor sit amet,
ius ex maiorum disputationi, in scaevola quaerendum nam."""

    options = {'pattern': pattern, 'match': 'exact'}
    expected = text

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_text_contains():
    pattern = """amet,
ius"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'contains'}

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert actual is None


def test_text_contains_replacement():
    pattern = """amet,
ius"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = 'a b c'
    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'contains', 'replacement': replacement}
    expected = """lOrEm iPsUm dOlOr sIt a b c eX MaIoRuM DiSpUtAtIoNi"""

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_text_contains_no_match():
    pattern = """amet,
ius"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'match': 'contains'}
    expected = text

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_text_startswith():
    pattern = """Lorem ipsum dolor sit amet,
ius"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'startswith'}

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert actual is None


def test_text_startswith_replacement():
    pattern = """Lorem ipsum dolor sit amet,
ius"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = 'a b c'
    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'startswith', 'replacement': replacement}
    expected = replacement + ' eX MaIoRuM DiSpUtAtIoNi'

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_text_startswith_no_match():
    pattern = """ipsum dolor sit amet,
ius"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'startswith'}
    expected = text

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_text_endswith():
    pattern = """amet,
ius ex maiorum disputationi"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'endswith'}

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert actual is None


def test_text_endswith_replacement():
    pattern = """amet,
ius ex maiorum disputationi"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = 'a b c'
    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'endswith', 'replacement': replacement}
    expected = 'lOrEm iPsUm dOlOr sIt ' + replacement

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_text_endswith_no_match():
    pattern = """ipsum dolor sit amet,
ius"""
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'flags': ['ignorecase'], 'match': 'startswith'}
    expected = text

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_exact():
    pattern = r'Lorem\b.*\bdisputationi'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'exact'}

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert actual is None


def test_regex_exact_replacement():
    pattern = r'Lorem\b.*\bdisputationi'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = 'a b c'
    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'exact',
               'replacement': replacement}
    expected = replacement

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_exact_replacement_with_groups():
    pattern = r'Lorem((\W*\w*)+)disputationi'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = r'Start\1End'
    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'exact',
               'replacement': replacement}
    expected = """Start iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM End"""

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_exact_no_match():
    pattern = r'Lorem\b.*\bdisputationi'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'type': 'regex', 'flags': ['dotall'], 'match': 'exact'}
    expected = text

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_contains():
    pattern = r'amet\b.*\bius'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'contains'}

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert actual is None


def test_regex_contains_replacement():
    pattern = r'amet\b.*\bius'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = 'a b c'
    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'contains',
               'replacement': replacement}
    expected = 'lOrEm iPsUm dOlOr sIt a b c eX MaIoRuM DiSpUtAtIoNi'

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_contains_replacement_with_groups():
    pattern = r'(sit)((?:\W*\w*)+)(ex)'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = r'a=\1 b=\3 c=\2'
    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'contains',
               'replacement': replacement}
    expected = """lOrEm iPsUm dOlOr a=sIt b=eX c= aMeT,
iUs  MaIoRuM DiSpUtAtIoNi"""

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_contains_no_match():
    pattern = r'amet\b.*\bius'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'type': 'regex', 'flags': ['dotall'], 'match': 'contains'}
    expected = text

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_startswith():
    pattern = r'Lorem\b.*\bius'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'startswith'}

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert actual is None


def test_regex_startswith_replacement():
    pattern = r'Lorem\b.*\bius'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = 'a b c'
    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'startswith',
               'replacement': replacement}
    expected = replacement + ' eX MaIoRuM DiSpUtAtIoNi'

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_startswith_replacement_with_groups():
    pattern = r'(Lorem)(\b.*\b)(ius)'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = r'a=\1 b=\3 c=\2'
    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'contains',
               'replacement': replacement}
    expected = """a=lOrEm b=iUs c= iPsUm dOlOr sIt aMeT,
 eX MaIoRuM DiSpUtAtIoNi"""

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_startswith_no_match():
    pattern = r'amet\b.*\bius'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'startswith'}
    expected = text

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_endswith():
    pattern = r'amet\b.*\bdisputationi'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'endswith'}

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert actual is None


def test_regex_endswith_replacement():
    pattern = r'amet\b.*\bdisputationi'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = 'a b c'
    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'endswith',
               'replacement': replacement}
    expected = 'lOrEm iPsUm dOlOr sIt ' + replacement

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_endswith_replacement_with_groups():
    pattern = r'(sit)\W+(amet)(\b.*\b)(disputationi)'
    text = """AMET lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    replacement = r'a=\1 \2 b=\4 c=\3'
    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'endswith',
               'replacement': replacement}
    expected = """AMET lOrEm iPsUm dOlOr a=sIt aMeT b=DiSpUtAtIoNi c=,
iUs eX MaIoRuM """

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual


def test_regex_endswith_no_match():
    pattern = r'Lorem\b.*\bius'
    text = """lOrEm iPsUm dOlOr sIt aMeT,
iUs eX MaIoRuM DiSpUtAtIoNi"""

    options = {'pattern': pattern, 'type': 'regex', 'flags': ['ignorecase', 'dotall'], 'match': 'endswith'}
    expected = text

    rule = Rule.from_config(options)
    actual = rule.apply(text)

    assert expected == actual
