# -*- coding: utf-8 -*-
import os
import re
from typing import List, Collection

import logging

from . import __title__, __author__
from .data import default_config_resources
from .rule import Rule, Rules
from .utils import load_config_file, merge_options, load_config_resource

from appdirs import AppDirs
from babelfish import Language

logger = logging.getLogger(__name__)
here = os.path.abspath(os.path.dirname(__file__))

FILENAME_RE = re.compile(r'^cleanit(-[\w-]+)?(\.\w+(-\w+){0,2})?.(ya?ml|json)$')


def get_default_config_files():
    dirs = AppDirs(appname=__title__, appauthor=__author__)
    folders = [dirs.site_config_dir, dirs.user_config_dir]

    locations = []
    for folder in folders:
        try:
            locations.extend([os.path.abspath(os.path.join(folder, f)) for f in os.listdir(folder) if FILENAME_RE.search(f)])
        except FileNotFoundError as e:
            logger.debug(f"Discarding location '{folder}'. {str(e)}")

    return locations


def load_configuration(*locations: str):
    configurations = []
    for location in locations:
        data = load_config_file(location)
        configurations.append(data)
        logger.debug(f'Loaded configuration from {location}')
    return configurations


def load_default_resources():
    configurations = []
    for resource in default_config_resources:
        data = load_config_resource(f'data/{resource}')
        configurations.append(data)
        logger.debug(f'Loaded configuration from {resource}')
    return configurations


default_config = merge_options(*(load_default_resources() + load_configuration(*get_default_config_files())))


class Config:
    def __init__(self, *args: dict):
        self.data = merge_options(default_config, *args)
        aliases = self.data.get('aliases', {})
        rules: List[Rule] = []

        for name, r in self.data.get('rules', {}).items():
            rules.append(Rule(name=name, aliases=aliases, **r))

        rules.sort(key=lambda s: s.priority, reverse=True)
        self.rules = rules

    @classmethod
    def from_path(cls, path: str = None):
        folders = [path] if path and os.path.isdir(path) else []
        locations = [path] if path and os.path.isfile(path) else []

        for folder in folders:
            locations.extend([f for f in os.listdir(folder) if FILENAME_RE.search(f)])

        return Config(*load_configuration(*locations))

    def select_rules(self, tags: Collection[str] = None, languages: Collection[Language] = None):
        return Rules(rules=self.rules, tags=tags, languages=languages)
