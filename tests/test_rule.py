# -*- coding: utf-8 -*-
from typing import Optional
import pytest

from cleanit.config import Config, Rule


def generate_params():
    config = Config()
    params = []
    for rule in config.rules:
        for text, expected in rule.examples.items():
            params.append((rule, text, expected))

    return params


@pytest.mark.parametrize('rule,text,expected', generate_params())
def test_default_rule(rule: Rule, text: str, expected: Optional[str]):
    # given
    # when
    actual = rule.apply(text)[0]
    # then
    assert actual == expected
