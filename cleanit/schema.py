# -*- coding: utf-8 -*-
from typing import List


def string_enum(values: List[str]):
    return {'type': 'string', 'enum': values}


def array(schema: dict, min_items=0):
    return {'type': 'array', 'items': schema, 'minItems': min_items}


def one_of(*schemas: dict):
    return {'oneOf': list(schemas)}


def one_or_array(schema: dict):
    return one_of(schema, array(schema, min_items=1))


class TagsSchema:
    schema = {'type': 'string'}


class RuleTypeSchema:
    schema = string_enum(['text', 'regex'])


class MatchTypeSchema:
    schema = string_enum(['exact', 'contains', 'startswith', 'endswith'])


class FlagSchema:
    schema = string_enum(['ignorecase', 'dotall', 'multiline', 'locale', 'unicode', 'verbose'])


class ReplacementSchema:
    schema = {'type': 'string'}


class PrioritySchema:
    schema = {'type': 'integer'}


class LanguageSchema:
    schema = {'type': 'string'}


class AliasesSchema:
    schema = {
        'type': 'object',
        'patternProperties': {
            '.+': {'type': 'string'}
        },
        'minProperties': 1
    }


class ExampleSchema:
    schema = one_of(array({'type': 'string'}, min_items=1),
                    {'type': 'object',
                     'patternProperties': {
                         '.+': {'type': ['string', 'null']}
                     },
                     'minProperties': 1
                     })


class RuleSchema:
    schema = {
        'type': 'object',
        'properties': {
            'type': RuleTypeSchema.schema,
            'match': MatchTypeSchema.schema,
            'flags': one_or_array(FlagSchema.schema),
            'tags': one_or_array(TagsSchema.schema),
            'priority': PrioritySchema.schema,
            'languages': one_or_array(LanguageSchema.schema),
            'patterns': one_or_array({'type': 'string'}),
            'disabled': {'type': ['boolean', 'null']},
            'replacement': ReplacementSchema.schema,
            'examples': ExampleSchema.schema
        },
        'additionalProperties': False
    }


class RulesSchema:
    schema = {
        'type': 'object',
        'patternProperties': {
            '.+': RuleSchema.schema
        },
        'minProperties': 1
    }


class RootSchema:
    schema = {
        'type': 'object',
        'properties': {
            'aliases': AliasesSchema.schema,
            'templates': array(RuleSchema.schema, min_items=0),
            'rules': RulesSchema.schema
        },
        'additionalProperties': False
    }
