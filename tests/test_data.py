from pathlib import Path

import pysrt
import pytest
import yaml

from cleanit.config import Config
from cleanit.rule import Rules
from cleanit.subtitle import Subtitle, get_subtitle_language

cases_path = Path(__file__).parent / "data" / "cases"


def _reformat(srt_path: Path) -> None:
    """Normalize a fixture through pysrt so its on-disk formatting matches what Subtitle.content produces."""
    srt = pysrt.open(str(srt_path))
    srt.clean_indexes()
    srt.save()


def generate_params():
    cfg = Config()
    params = []
    for case_dir in sorted(p for p in cases_path.iterdir() if p.is_dir()):
        meta = yaml.safe_load((case_dir / "meta.yaml").read_text(encoding="utf-8"))
        tags = set(meta.get("tags", []))

        # the language is carried by the filename itself (e.g. input.pt-BR.srt), exactly like
        # Subtitle does for real files, so a case can never drift out of sync with what it tests.
        (input_file,) = case_dir.glob("input.*.srt")
        (expected_file,) = case_dir.glob("expected.*.srt")
        _reformat(input_file)
        _reformat(expected_file)

        rules = cfg.select_rules(tags=tags, languages={get_subtitle_language(str(input_file))})
        params.append(pytest.param(rules, input_file, expected_file, id=case_dir.name))

    return params


@pytest.mark.parametrize("rules,input_file,expected_file", generate_params())
def test_data_files(rules: Rules, input_file: Path, expected_file: Path) -> None:
    # given
    subtitle = Subtitle(str(input_file))
    expected_text = expected_file.read_text(encoding="utf-8").strip()
    # when
    subtitle.clean(rules)
    # then
    assert subtitle.content == expected_text
