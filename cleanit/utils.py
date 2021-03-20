import copy
import json
import pkgutil
from types import GeneratorType
from typing import Any, Set

import jsonschema
import yaml
from babelfish import Language

from .schema import RootSchema


def is_iterable(obj: Any):
    return hasattr(obj, '__iter__') and not isinstance(obj, str) or isinstance(obj, GeneratorType)


def ensure_list(param: Any):
    if not param:
        param = []
    elif not is_iterable(param):
        param = [param]
    return param


def get_language_groups(languages: Set[Language]):
    groups = set()
    for language in languages:
        ietf = str(language)
        ietf_parts = ietf.split('-')

        groups.add(ietf)
        groups.add(ietf_parts[0])
        groups.add('-'.join(ietf_parts[:2]))

    return groups


def validate(data: dict):
    jsonschema.validate(data, RootSchema.schema)


def load_config_file(path: str):
    with open(path, 'r') as f:
        data = json.load(f) if path.endswith('.json') else yaml.safe_load(f.read())
    validate(data)
    return data


def load_config_resource(resource_name: str):
    resource_data = pkgutil.get_data('cleanit', resource_name)
    data = json.loads(resource_data) if resource_name.endswith('.json') else yaml.safe_load(resource_data)
    validate(data)
    return data


def merge_options(*options):
    """
    Merge options into a single options dict.
    :param options:
    :type options:
    :return:
    :rtype:
    """

    merged = {}
    if options:
        if options[0]:
            merged.update(copy.deepcopy(options[0]))

        for options in options[1:]:
            if options:
                pristine = options.get('pristine')

                if pristine is True:
                    merged = {}
                elif pristine:
                    for to_reset in pristine:
                        if to_reset in merged:
                            del merged[to_reset]

                for (option, value) in options.items():
                    merge_option_value(option, value, merged)

    return merged


def merge_option_value(option, value, merged):
    """
    Merge option value
    :param option:
    :param value:
    :param merged:
    :return:
    """
    if value is not None and option != 'pristine':
        if option in merged.keys() and isinstance(merged[option], list):
            for val in value:
                if val not in merged[option] and val is not None:
                    merged[option].append(val)
        elif option in merged.keys() and isinstance(merged[option], dict):
            merged[option] = merge_options(merged[option], value)
        elif isinstance(value, list):
            merged[option] = list(value)
        else:
            merged[option] = value
