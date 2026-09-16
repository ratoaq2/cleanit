import copy
import json
import pkgutil
from types import GeneratorType
from typing import Any

import jsonschema
import yaml
from babelfish import Language

from .schema import RootSchema


def is_iterable(obj: Any) -> bool:
    return hasattr(obj, "__iter__") and not isinstance(obj, str) or isinstance(obj, GeneratorType)


def ensure_list(param: Any) -> list[Any]:
    if not param:
        param = []
    elif not is_iterable(param):
        param = [param]
    return list(param)


def get_language_groups(languages: set[Language]) -> set[str]:
    groups = set()
    for language in languages:
        ietf = str(language)
        ietf_parts = ietf.split("-")

        groups.add(ietf)
        groups.add(ietf_parts[0])
        groups.add("-".join(ietf_parts[:2]))

    return groups


def validate(data: dict[str, Any]) -> None:
    jsonschema.validate(data, RootSchema.schema)


def load_config_file(path: str) -> dict[str, Any]:
    with open(path) as f:
        data: dict[str, Any] = json.load(f) if path.endswith(".json") else yaml.safe_load(f.read())
    validate(data)
    return data


def load_config_resource(resource_name: str) -> dict[str, Any]:
    resource_data = pkgutil.get_data("cleanit", resource_name)
    if resource_data is None:
        raise FileNotFoundError(f"Resource '{resource_name}' could not be found in package 'cleanit'")
    data: dict[str, Any] = (
        json.loads(resource_data) if resource_name.endswith(".json") else yaml.safe_load(resource_data)
    )
    validate(data)
    return data


def merge_options(*options: dict[str, Any] | None) -> dict[str, Any]:
    """
    Merge options into a single options dict.
    :param options:
    :type options:
    :return:
    :rtype:
    """

    merged: dict[str, Any] = {}
    if options:
        if options[0]:
            merged.update(copy.deepcopy(options[0]))

        for extra_options in options[1:]:
            if extra_options:
                pristine = extra_options.get("pristine")

                if pristine is True:
                    merged = {}
                elif pristine:
                    for to_reset in pristine:
                        if to_reset in merged:
                            del merged[to_reset]

                for option, value in extra_options.items():
                    merge_option_value(option, value, merged)

    return merged


def merge_option_value(option: str, value: Any, merged: dict[str, Any]) -> None:
    """
    Merge option value
    :param option:
    :param value:
    :param merged:
    :return:
    """
    if value is not None and option != "pristine":
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
