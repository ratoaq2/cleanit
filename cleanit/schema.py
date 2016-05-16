# -*- coding: utf-8 -*-

rule_type = {'type': 'string', 'enum': ['text', 'regex']}
match_type = {'type': 'string', 'enum': ['exact', 'contains', 'startswith', 'endswith']}
whitelist = {'type': 'boolean'}
flag = {'type': 'string', 'enum': ['ignorecase', 'dotall', 'multiline', 'locale', 'unicode', 'verbose']}
flags = {'oneOf': [flag, {'type': 'array', 'items': flag}]}
replacement_type = {'type': 'string'}

rule_tuple_string_string = {
    'type': 'object',
    'patternProperties': {
        '.+': {'type': 'string'}
    },
    'minProperties': 1,
    'maxProperties': 1
}
rule_tuple_string_dict = {
    'type': 'object',
    'patternProperties': {
        '.+': {
            'type': 'object',
            'properties': {
                'replacement': replacement_type,
                'type': rule_type,
                'match': match_type,
                'flags': flags,
                'whitelist': whitelist
            },
            'additionalProperties': False
        }
    },
    'minProperties': 1,
    'maxProperties': 1
}

rule = {'anyOf': [{'type': 'string'}, rule_tuple_string_string, rule_tuple_string_dict]}
rules = {'type': 'array', 'items': rule, 'minItems': 1, 'uniqueItems': True}

group = {
    'type': 'object',
    'properties': {
        'template': {'type': 'string'},
        'type': rule_type,
        'match': match_type,
        'flags': flags,
        'whitelist': whitelist,
        'rules': rules
    },
    'required': ['rules'],
    'additionalProperties': False
}

groups = {
    'type': 'object',
    'patternProperties': {
        '.+': group
    },
    'minProperties': 1
}

template = {
    'type': 'object',
    'properties': {
        'type': rule_type,
        'match': match_type,
        'flags': flags,
        'replacement': replacement_type,
        'whitelist': whitelist
    },
    'additionalProperties': False
}
templates = {
    'type': 'object',
    'patternProperties': {
        '.+': template
    },
    'minProperties': 1
}

root = {
    'type': 'object',
    'properties': {
        'templates': templates,
        'groups': groups
    },
    'additionalProperties': False
}
