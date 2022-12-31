# -*- coding: utf-8 -*-
import logging
import re
from collections import UserList
from typing import Optional, Collection, Dict, Tuple, Set, Iterable, List

from babelfish import Language
from pysrt import SubRipItem, SubRipFile

from .utils import ensure_list, get_language_groups

logger = logging.getLogger(__name__)


class Change:
    def __init__(self, item: SubRipItem):
        self._max_chars = 50
        self.start = item.start
        self.end = item.end
        self.a_lines = [line for line in item.text.split('\n')]
        self.b_lines = self.a_lines
        self.rules: List[str] = []

    def track(self, rule: str, text: Optional[str]):
        self.rules.append(rule)
        self.b_lines = [line for line in text.split('\n')] if text else []

    @property
    def timestamp(self):
        return f'{self.start} --> {self.end}'

    @property
    def rules_description(self):
        return ' '.join(r for r in self.rules)

    @property
    def max_chars(self):
        return max(self._max_chars, (len(self.rules_description) // 2 + 1),
                   *[len(line) for line in self.a_lines + self.b_lines])

    @max_chars.setter
    def max_chars(self, value: int):
        self._max_chars = max(self._max_chars, value)

    def get_line_tuples(self):
        a_lines = self.a_lines + [''] * (len(self.b_lines) - len(self.a_lines))
        b_lines = self.b_lines + [''] * (len(self.a_lines) - len(self.b_lines))
        for a, b in zip(a_lines, b_lines):
            yield a, b

    def __repr__(self):
        return f'<{self.__class__.__name__} [{self.timestamp} ({self.rules_description})]>'

    def __str__(self):
        max_width = self.max_chars * 2 + 1
        lines = [
            f'<{self.rules_description}>'.center(max_width),
            f'{self.timestamp.center(max_width//2)} {self.timestamp.center(max_width//2)}'
        ]
        for a, b in self.get_line_tuples():
            line = f'{a.center(max_width//2)}|{b.center(max_width//2)}'
            lines.append(line)

        return '\n'.join(lines)


class Changes(UserList):

    def __init__(self, srt: SubRipFile):
        super().__init__()
        self.path = srt.path

    def __repr__(self):
        return f'<{self.__class__.__name__} [{self.path}:{len(self)}]>'

    def __str__(self):
        lines = [f'{self.path}']
        for item in self:
            lines.append(str(item))

        return '\n\n'.join(lines) + '\n'


class Rule:
    def __init__(self, name: str, aliases: Dict[str, str], patterns: Collection[str] or str, type: str = 'regex',
                 match: str = 'contains', priority: int = 0, tags: Optional[Collection[str] or str] = None,
                 flags: Optional[Collection[str] or str] = None, languages: Optional[Collection[str] or str] = None,
                 replacement: Optional[str] = None, examples: Optional[Dict[str, str] or str] = None, disabled=False):
        self.name = name
        re_flags = 0
        r_flags = set(ensure_list(flags))
        for flag in r_flags:
            re_flags |= re.__dict__.get(flag.upper())

        regexes = []
        for pattern in ensure_list(patterns):
            re_pattern: str = pattern if type == 'regex' else re.escape(pattern)
            if type == 'regex':
                for k, v in aliases.items():
                    re_pattern = re_pattern.replace(k, v)

            if match in ('endswith', 'exact'):
                re_pattern = f'{re_pattern}$'
            if match in ('startswith', 'exact'):
                re_pattern = f'^{re_pattern}'
            regexes.append(re.compile(re_pattern, re_flags))

        self.regexes = regexes
        self.flags = r_flags
        self.priority = priority
        self.tags = set(ensure_list(tags))
        self.disabled = disabled
        self.languages = {Language.fromietf(lang) for lang in ensure_list(languages)}
        self.language_groups = get_language_groups(self.languages)
        self.replacement = replacement
        self.examples = {key.strip(): value.strip() if value is not None else None for key, value in
                         (examples if isinstance(examples, dict) else (
                             {e: None for e in examples} if isinstance(examples, list) else {})).items()}

    def __repr__(self):
        return f'<{self.__class__.__name__} [{str(self)}]>'

    def __str__(self):
        return self.name

    def matches(self, tags: Set[str] = None, languages: Set[Language] = None):
        if self.disabled:
            return False

        tags = tags or set()
        if self.tags and not self.tags.intersection(tags) and 'all' not in tags:
            return False

        if not self.languages or not languages:
            return True

        language_groups = get_language_groups(languages)

        return self.language_groups.intersection(language_groups)

    def apply(self, text: str or None, replacement: str = None, change: Change = None):
        for regex in self.regexes:
            m = regex.search(text)
            if not m:
                continue

            repl = replacement or self.replacement
            if repl is None:
                if change:
                    change.track(self.name, None)
                return None, True

            value = regex.sub(repl, text).strip() or None
            if change:
                change.track(self.name, value or None)

            if not value:
                return None, True

            return self.apply(value, replacement=replacement, change=change)[0], True

        return text, False


class Rules(UserList):

    def __init__(self, rules: Iterable[Rule], tags: Set[str] = None, languages: Set[Language] = None):
        self.tags = tags or set()
        self.languages = languages or set()
        super().__init__([r for r in rules if r.matches(tags=self.tags, languages=self.languages)])

    def __repr__(self):
        return f'<{self.__class__.__name__} [{self.languages}:{self.tags}:{len(self)}]>'

    def apply(self, value: str, replacement: str = None, change: Change = None) -> Tuple[Optional[str], bool]:
        result = value
        modified = False
        for rule in self:
            previous = result
            result, matches = rule.apply(previous, replacement=replacement, change=change)
            if matches:
                modified = True
                if not result:
                    return result, modified
                else:
                    break

        if modified:
            return self.apply(result, replacement=replacement, change=change)[0], True

        return result, modified

    def clean(self, value: str, replacement=''):
        return self.apply(value, replacement=replacement)[0]
