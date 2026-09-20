import pytest
from babelfish import Language

from cleanit.subtitle import NON_LANGUAGE_CODES, get_subtitle_language


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
