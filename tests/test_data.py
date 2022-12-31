# -*- coding: utf-8 -*-
import glob
import os
import re

import pysrt
import pytest
from babelfish import Language

from cleanit.config import Config
from cleanit.rule import Rules
from cleanit.subtitle import Subtitle

data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def generate_params():
    cfg = Config()
    f_re = re.compile(r'(?P<id>\d{3})\.B(?P<tags>(?:\.[-\w]+)*)\.(?P<lang>[a-zA-Z-]+)\.srt')
    expected_files = glob.glob(os.path.join(data_path, '[0-9][0-9][0-9].B.*.srt'))
    params = []
    for f in expected_files:
        folder, filename = os.path.split(f)
        matches = f_re.match(filename).groupdict()
        f_id = int(matches.get('id'))
        tags = {t for t in matches.get('tags', '').split('.') if t}
        f_lang = Language.fromietf(matches.get('lang'))
        input_file = os.path.join(folder, f'{f_id:03d}.A.{str(f_lang)}.srt')
        for s in (input_file, f):
            srt = pysrt.open(s)
            srt.clean_indexes()
            srt.save()
        params.append((cfg.select_rules(tags=tags, languages={f_lang}), input_file, f))

    return params


@pytest.mark.parametrize('rules,input_file,expected_file', generate_params())
def test_data_files(rules: Rules, input_file, expected_file):
    # given
    subtitle = Subtitle(input_file)
    with open(expected_file, 'r', encoding='utf8') as f:
        expected_text = f.read().strip()
    # when
    subtitle.clean(rules)
    # then

    assert subtitle.content == expected_text
