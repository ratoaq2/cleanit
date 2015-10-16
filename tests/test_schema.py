# -*- coding: utf-8 -*-

import jsonschema
import pytest

from cleanit import schema
from jsonschema.exceptions import ValidationError


def test_schema_valid_rule_types():
    json = ['text', 'regex']

    jsonschema.validate(json, {'type': 'array', 'items': schema.rule_type})


def test_schema_invalid_rule_types():
    json = ['invalid']

    with pytest.raises(ValidationError):
        jsonschema.validate(json, {'type': 'array', 'items': schema.rule_type})


def test_schema_valid_match_types():
    json = ['exact', 'contains', 'startswith', 'endswith']

    jsonschema.validate(json, {'type': 'array', 'items': schema.match_type})


def test_schema_invalid_match_types():
    json = ['invalid']

    with pytest.raises(ValidationError):
        jsonschema.validate(json, {'type': 'array', 'items': schema.match_type})


def test_schema_valid_flags():
    json = ['ignorecase', 'dotall', 'multiline', 'locale', 'unicode', 'verbose']

    jsonschema.validate(json, {'type': 'array', 'items': schema.flag})


def test_schema_invalid_flags():
    json = ['invalid']

    with pytest.raises(ValidationError):
        jsonschema.validate(json, {'type': 'array', 'items': schema.flag})


def test_schema_valid_single_flags():
    json = ['ignorecase']

    jsonschema.validate(json, {'type': 'array', 'items': schema.flags})


def test_schema_valid_array_flags():
    json = [['ignorecase', 'dotall', 'multiline', 'locale', 'unicode', 'verbose']]

    jsonschema.validate(json, {'type': 'array', 'items': schema.flags})


def test_schema_valid_simple_rule():
    json = ['simple_rule']

    jsonschema.validate(json, schema.rules)


def test_schema_invalid_empty_simple_rule():
    json = []

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.rules)


def test_schema_invalid_duplicated_simple_rule():
    json = ['simple_rule', 'simple_rule']

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.rules)


def test_schema_invalid_simple_rule():
    json = [2]

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.rules)


def test_schema_valid_rule_tuple_string_string():
    json = [{'simple_rule': 'simple_replacement'}]

    jsonschema.validate(json, schema.rules)


def test_schema_invalid_empty_rule_tuple_string_string():
    json = [{}]

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.rules)


def test_schema_invalid_rule_tuple_string_string():
    json = [{'simple_rule': 2}]

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.rules)


def test_schema_invalid_key_rule_tuple_string_string():
    json = [{3: 'simple_replacement'}]

    with pytest.raises(TypeError):
        jsonschema.validate(json, schema.rules)


def test_schema_valid_rule_tuple_string_dict():
    json = [{'rule one': {'replacement': 'the_replacement',
                          'type': 'text',
                          'match': 'startswith',
                          'whitelist': False,
                          'flags': 'ignorecase'}}]

    jsonschema.validate(json, schema.rules)


def test_schema_invalid_rule_tuple_string_dict():
    json = [{'rule one': {'replacement': 'the_replacement',
                          'type': 'text',
                          'match': 'startswith',
                          'flags': 'ignorecase',
                          'whitelist': False,
                          'unknown_property': 'unknown_value'}}]

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.rules)


def test_schema_invalid_rule_tuple_string_dict_invalid_values():
    json = [{'rule one': {'replacement': 'the_replacement',
                          'type': 'text',
                          'match': 'invalid_match',
                          'whitelist': False,
                          'flags': 'ignorecase'}}]

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.rules)


def test_schema_valid_rules():
    json = ['first rule',
            {'second rule': 'rule replacement'},
            {'third rule': {'replacement': 'the_replacement',
                            'type': 'text',
                            'match': 'startswith',
                            'whitelist': False,
                            'flags': 'ignorecase'}}]

    jsonschema.validate(json, schema.rules)


def test_schema_valid_template():
    json = {'template one': {'type': 'regex',
                             'match': 'contains',
                             'flags': ['dotall', 'ignorecase']}}

    jsonschema.validate(json, schema.templates)


def test_schema_invalid_template():
    json = {'template one': {'type': 'regex',
                             'match': 'contains',
                             'flags': ['dotall', 'ignorecase'],
                             'unknown_property': 'unknown_value'}}

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.templates)


def test_schema_invalid_empty_templates():
    json = {}

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.templates)


def test_schema_invalid_empty_template():
    json = {'template one': None}

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.templates)


def test_schema_valid_group():
    json = {'group name': {'template': 'common',
                           'type': 'regex',
                           'match': 'contains',
                           'whitelist': True,
                           'flags': ['dotall', 'ignorecase'],
                           'rules': ['rule one']}}

    jsonschema.validate(json, schema.groups)


def test_schema_invalid_group():
    json = {'group name': {'template': 'common',
                           'type': 'regex',
                           'match': 'contains',
                           'flags': ['dotall', 'ignorecase']}}

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.groups)


def test_schema_invalid_empty_groups():
    json = {}

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.groups)


def test_schema_invalid_empty_group():
    json = {'group name': None}

    with pytest.raises(ValidationError):
        jsonschema.validate(json, schema.templates)


def test_valid_schema():
    json = {'templates': {'template one': {'type': 'regex',
                                           'match': 'contains',
                                           'whitelist': True,
                                           'flags': ['dotall', 'ignorecase']},
                          'template two': {'type': 'text',
                                           'match': 'startswith',
                                           'whitelist': False,
                                           'flags': 'ignorecase'}
                          },
            'groups': {'group one': {'template': 'template two',
                                     'match': 'exact',
                                     'rules': ['Rule 1',
                                               {'Rule 2': 'replacement text'},
                                               {'Rule 3': {'replacement': 'replacement text',
                                                           'flags': 'ignorecase'}
                                                }]
                                     },
                       'group two': {'template': 'template one',
                                     'match': 'endswith',
                                     'rules': ['Rule 4',
                                               {'Rule 5': 'replacement text'},
                                               {'Rule 6': {'replacement': 'replacement text',
                                                           'flags': ['ignorecase']}
                                                }]
                                     },
                       }
            }

    jsonschema.validate(json, schema.root)
