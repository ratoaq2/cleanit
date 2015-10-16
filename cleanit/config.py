# -*- coding: utf-8 -*-
import os

import jsonschema
import logging
import yaml

from . import __title__, __author__, schema
from .rule import Rule

from appdirs import user_config_dir


logger = logging.getLogger(__name__)


class Config(object):

    def __init__(self, path):
        #: Path to the configuration file
        self.path = path
        self.json = None
        self.rules = None

    def load(self):
        with open(self.path, 'r') as ymlfile:
            self.json = yaml.safe_load(ymlfile)

    def consolidate(self):
        jsonschema.validate(self.json, schema.root)

        templates = self.json.get('templates', {})
        groups = self.json.get('groups', {})
        rules = []

        for name, group in groups.items():
            template_name = group.get('template')

            template = templates.get(template_name) if template_name else None
            if not template and template_name:
                raise ValueError("Template '%s' referenced in group '%s' does not exist" % (template_name, group))

            for rule in group.get('rules', []):
                target = {}
                flags = set([])
                if template:
                    target.update({k: v for k, v in template.items() if v and v != 'flags'})
                    flags |= set((lambda v: v if isinstance(v, list) else [v])(template.get('flags', [])))

                target.update({k: v for k, v in group.items() if v and k not in ['template', 'rules', 'flags']})
                flags |= set((lambda v: v if isinstance(v, list) else [v])(group.get('flags', [])))

                if isinstance(rule, dict):
                    pattern, rule_config = rule.items()[0]
                    target.update({'pattern': pattern})
                    if isinstance(rule_config, dict):
                        target.update({k: v for k, v in rule_config.items() if v and v != 'flags'})
                        flags |= set((lambda v: v if isinstance(v, list) else [v])(rule_config.get('flags', [])))
                    else:
                        target.update({'replacement': rule_config})
                else:
                    target.update({'pattern': rule})

                if target:
                    target.update({'flags': list(flags)})
                    rules.append(Rule.from_config(target))

        if not rules:
            raise ValueError("No rules defined in config file '%s'" % self.path)

        # Whitelist rules should come first
        rules.sort(key=lambda s: s.whitelist, reverse=True)

        self.rules = rules

    @staticmethod
    def from_file(path=None):
        file_name = 'config.yml'

        locations = [path, os.path.join(path, file_name)] if path else []
        locations += [os.path.join(user_config_dir(appname=__title__, appauthor=__author__), file_name)]

        for location in locations:
            if os.path.isfile(location):
                try:
                    config = Config(location)
                    config.load()
                    config.consolidate()

                    return config
                except IOError as e:
                    logger.warn("Ignoring invalid configuration file '%s'. %s" % (location, str(e)))
