from pathlib import Path

import pytest

from cleanit.config import Config


def test_from_path_reads_rule_files_in_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "cleanit-custom.yml").write_text("rules:\n  my-rule[custom]:\n    tags: ocr\n    patterns: x\n")
    monkeypatch.chdir(tmp_path.parent)

    cfg = Config.from_path(str(tmp_path))

    assert "my-rule[custom]" in {r.name for r in cfg.rules}
