import logging
from pathlib import Path

import pytest
from babelfish import Language

from cleanit.config import Config
from cleanit.subtitle import NON_LANGUAGE_CODES, Subtitle, get_subtitle_language


@pytest.mark.parametrize(
    "path, expected",
    [
        ("movie.en.srt", "en"),
        ("movie.pt-BR.srt", "pt-BR"),
        ("movie.srt", "und"),
    ],
)
def test_get_subtitle_language(path: str, expected: str) -> None:
    assert get_subtitle_language(path) == Language.fromietf(expected)


@pytest.mark.parametrize("code", sorted(NON_LANGUAGE_CODES))
def test_get_subtitle_language_ignores_release_tags(code: str) -> None:
    assert get_subtitle_language(f"movie.{code}.srt") == Language("und")
    assert get_subtitle_language(f"movie.{code.upper()}.srt") == Language("und")


def clean_and_save(path: Path, data: bytes, tags: set[str]) -> bytes:
    path.write_bytes(data)
    subtitle = Subtitle(str(path))
    rules = Config().select_rules(tags=tags, languages={subtitle.language})
    assert subtitle.clean(rules)
    subtitle.save()
    return path.read_bytes()


@pytest.mark.parametrize("eol", ["\r\n", "\n"])
def test_save_keeps_line_ending(tmp_path: Path, eol: str) -> None:
    data = "1\n00:00:01,000 --> 00:00:02,000\n-Where is he?\n-Here.\n\n".replace("\n", eol)
    expected = "1\n00:00:01,000 --> 00:00:02,000\n- Where is he?\n- Here.\n\n".replace("\n", eol)

    assert clean_and_save(tmp_path / "movie.en.srt", data.encode(), {"tidy"}) == expected.encode()


def test_save_keeps_tags(tmp_path: Path) -> None:
    tagged = (
        "2\n00:00:03,000 --> 00:00:04,000\n{\\an8}<b>Bold words</b>\n\n"
        '3\n00:00:05,000 --> 00:00:06,000\n<font color="#fff">Colored words</font>\n\n'
        "4\n00:00:07,000 --> 00:00:08,000\n<Invented aside>\n<i>Italic words</i>\n\n"
    )
    data = "1\n00:00:01,000 --> 00:00:02,000\n-Where is he?\n-Here.\n\n" + tagged

    assert clean_and_save(tmp_path / "movie.en.srt", data.encode(), {"tidy"}).decode().endswith(tagged)


def test_clean_does_not_join_line_with_trailing_space(tmp_path: Path) -> None:
    data = "1\n00:00:01,000 --> 00:00:02,000\nVamos falar \ncom a vizinha.\n\n"
    expected = "1\n00:00:01,000 --> 00:00:02,000\nVamos falar\ncom a vizinha.\n\n"
    data += "2\n00:00:03,000 --> 00:00:04,000\n-Sim.\n-Não.\n\n"
    expected += "2\n00:00:03,000 --> 00:00:04,000\n- Sim.\n- Não.\n\n"

    tags = {"ocr", "tidy", "no-sdh", "no-lyrics", "no-spam"}
    assert clean_and_save(tmp_path / "movie.pt-BR.srt", data.encode(), tags) == expected.encode()


def test_clean_sorts_entries_by_time(tmp_path: Path) -> None:
    data = "1\n00:00:03,000 --> 00:00:04,000\n-Later.\n-Yes.\n\n2\n00:00:01,000 --> 00:00:02,000\nEarlier.\n\n"
    expected = "1\n00:00:01,000 --> 00:00:02,000\nEarlier.\n\n2\n00:00:03,000 --> 00:00:04,000\n- Later.\n- Yes.\n\n"

    assert clean_and_save(tmp_path / "movie.en.srt", data.encode(), {"tidy"}) == expected.encode()


def test_save_keeps_encoding(tmp_path: Path) -> None:
    data = "1\n00:00:01,000 --> 00:00:02,000\n-A criança está aqui.\n-Sim.\n\n"
    expected = "1\n00:00:01,000 --> 00:00:02,000\n- A criança está aqui.\n- Sim.\n\n"

    assert clean_and_save(tmp_path / "movie.pt-BR.srt", data.encode("latin-1"), {"tidy"}) == expected.encode("latin-1")


def test_clean_loses_last_line_with_only_a_number_in_last_entry(tmp_path: Path) -> None:
    # known pysubs2 limit: the reader takes this line for the index of a next entry
    first = "1\n00:00:01,000 --> 00:00:02,000\nInvented Town\n1963\n\n"
    data = first + "2\n00:00:03,000 --> 00:00:04,000\n-Yes.\n-No.\n\n"
    data += "3\n00:00:05,000 --> 00:00:06,000\nInvented Town\n1963\n\n"
    expected = first + "2\n00:00:03,000 --> 00:00:04,000\n- Yes.\n- No.\n\n"
    expected += "3\n00:00:05,000 --> 00:00:06,000\nInvented Town\n\n"

    assert clean_and_save(tmp_path / "movie.en.srt", data.encode(), {"tidy"}) == expected.encode()


def test_clean_logs_changes(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    data = "1\n00:00:01,000 --> 00:00:02,000\n-Where is he?\n-Here.\n\n"

    with caplog.at_level(logging.DEBUG, logger="cleanit"):
        clean_and_save(tmp_path / "movie.en.srt", data.encode(), {"tidy"})

    assert "00:00:01,000 --> 00:00:02,000" in caplog.text
    assert "-Where is he?" in caplog.text
    assert "- Where is he?" in caplog.text
