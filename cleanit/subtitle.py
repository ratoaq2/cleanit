import logging
import os
from io import StringIO

import chardet
from babelfish import Language, LanguageReverseConverter, LanguageReverseError, country_converters, language_converters
from pysubs2 import SSAFile
from pysubs2.formats.subrip import SubripFormat

from .rule import Change, Changes, Rules

logger = logging.getLogger(__name__)


# Release tags that also happen to be valid but obscure ISO 639-3 codes with no ISO 639-1
# equivalent. A subtitle filename ending in one of these almost always carries over a leftover
# release/media tag from the video file it was ripped from, not an actual language.
# See https://github.com/ratoaq2/pgsrip/issues/116 and cleanit/knowit's media codec lists at
# https://github.com/ratoaq2/knowit/blob/main/knowit/defaults.yml
NON_LANGUAGE_CODES = {
    "aac",  # AAC audio codec (vs Ari)
    "asp",  # MPEG-4 ASP video codec (vs Algerian Sign Language)
    "ass",  # Advanced SubStation Alpha subtitle format (vs Ipulo)
    "cbr",  # constant bit rate (vs Cashibo-Cacataibo)
    "dts",  # DTS audio codec (vs Toro So Dogon)
    "hra",  # DTS-HD HRA audio profile (vs Hrangkhol)
    "low",  # video profile level (vs Tampias Lobu)
    "pcm",  # PCM audio codec (vs Nigerian Pidgin)
    "pgs",  # Presentation Graphic Stream subtitle format (vs Pangseng)
    "png",  # image-based subtitle track (vs Pongu)
    "pro",  # audio profile / Professional (vs Old Provençal)
    "srt",  # SubRip subtitle format (vs Sauri)
    "sdh",  # Subtitles for Deaf and Hard of hearing (vs Southern Kurdish)
    "sdr",  # Standard Dynamic Range (vs Oraon Sadri)
}


class CleanitLanguageConverter(LanguageReverseConverter):  # type: ignore[misc]
    @property
    def codes(self) -> set[str]:
        codes: set[str] = (
            language_converters["alpha3b"].codes
            | language_converters["alpha2"].codes
            | language_converters["name"].codes
            | language_converters["opensubtitles"].codes
            | country_converters["name"].codes
        )
        return codes

    def convert(self, alpha3: str, country: str | None = None, script: str | None = None) -> str:
        return str(Language(alpha3, country, script))

    def reverse(self, name: str) -> tuple[str, str | None, str | None]:
        name = name.lower()
        if name in NON_LANGUAGE_CODES:
            return "und", None, None

        for conv in [
            Language.fromietf,
            Language,
            Language.fromalpha3b,
            Language.fromalpha2,
            Language.fromname,
            Language.fromopensubtitles,
        ]:
            try:
                reverse = conv(name)
                return reverse.alpha3, reverse.country, reverse.script
            except (ValueError, LanguageReverseError):
                pass

        return "und", None, None


language_converters["cleanit"] = CleanitLanguageConverter()


def get_subtitle_language(path: str) -> Language:
    lang = os.path.splitext(os.path.splitext(path)[0])[1] or ".und"
    return Language.fromcleanit(lang[1:])


class Subtitle:
    def __init__(self, path: str, encoding: str | None = None):
        self.path = path
        self.language = get_subtitle_language(path)
        self.encoding = encoding
        self.eol: str = os.linesep
        self._subtitle: SSAFile | None = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{self.path}]>"

    @property
    def content(self) -> str | None:
        if self._subtitle:
            return self._subtitle.to_string("srt", keep_ssa_tags=True).strip()
        return None

    @property
    def name(self) -> str:
        return os.path.split(self.path)[1]

    def match(self, languages: set[Language]) -> bool:
        return not languages or self.language in languages

    def save(self, path: str | None = None, encoding: str | None = None) -> None:
        if self._subtitle is None:
            raise RuntimeError(f"Subtitle {self.name} has not been loaded yet, call clean() first")
        with open(path or self.path, "w", encoding=encoding or self.encoding, newline=self.eol) as f:
            self._subtitle.to_file(f, "srt", keep_ssa_tags=True)

    def _read(self) -> SSAFile:
        with open(self.path, encoding=self.encoding, newline="") as f:
            text = f.read()

        # keep the line ending of the first line, as pysrt did
        first_line = next(iter(text.splitlines(keepends=True)), "")
        self.eol = next((eol for eol in ("\r\n", "\r", "\n") if first_line.endswith(eol)), os.linesep)

        # newline=None reads "\r\n" and "\r" as "\n". keep_html_tags keeps <i>, <font>, and <text> as they are
        subtitle = SSAFile.from_file(StringIO(text, newline=None), "srt", keep_html_tags=True)
        for event in subtitle:
            event.text = "\\N".join(line.rstrip() for line in event.text.split("\\N"))

        return subtitle

    def guess_encoding(self) -> str | None:
        with open(self.path, "rb") as f:
            content = f.read()

        # always try utf-8 first
        encodings = ["utf-8"]

        # add language-specific encodings
        if self.language.alpha3 == "zho":
            encodings.extend(["gb18030", "big5"])
        elif self.language.alpha3 == "jpn":
            encodings.append("shift-jis")
        elif self.language.alpha3 == "ara":
            encodings.append("windows-1256")
        elif self.language.alpha3 == "heb":
            encodings.append("windows-1255")
        elif self.language.alpha3 == "tur":
            encodings.extend(["iso-8859-9", "windows-1254"])
        elif self.language.alpha3 == "pol":
            # Eastern European Group 1
            encodings.extend(["windows-1250"])
        elif self.language.alpha3 == "bul":
            # Eastern European Group 2
            encodings.extend(["windows-1251"])
        else:
            # Western European (windows-1252)
            encodings.append("latin-1")

        # try to decode
        for encoding in encodings:
            try:
                content.decode(encoding)
            except UnicodeDecodeError:
                pass
            else:
                return encoding

        logger.warning("Could not guess encoding from language")

        # fallback on chardet
        detected_encoding = chardet.detect(content)["encoding"]
        logger.info(f"Chardet found encoding {detected_encoding}")

        return detected_encoding

    def clean(self, rules: Rules, clean_indexes: bool = True) -> bool:
        rules = Rules(rules=rules, tags=rules.tags, languages={self.language})
        self.encoding = self.encoding or self.guess_encoding()
        self._subtitle = self._read()
        track_changes = logger.isEnabledFor(logging.DEBUG)
        changes = Changes(self.path) if track_changes else None

        modified = False
        for i, event in reversed(list(enumerate(self._subtitle))):
            # the rules use "\n" for a new line, pysubs2 uses \N
            text = event.text.replace("\\N", "\n")
            change = None
            if track_changes:
                start, end = SubripFormat.ms_to_timestamp(event.start), SubripFormat.ms_to_timestamp(event.end)
                change = Change(start, end, event.text.split("\\N"))
            cleaned, changed = rules.apply(text, change=change)
            if changed:
                modified = True
                if not cleaned:
                    del self._subtitle[i]
                else:
                    event.text = cleaned.replace("\n", "\\N")
                if track_changes:
                    assert changes is not None
                    assert change is not None
                    changes.append(change)

        if modified:
            if track_changes:
                assert changes is not None
                max_chars = max(c.max_chars for c in changes)
                for c in changes:
                    c.max_chars = max_chars

                logger.debug(f"Changes for {changes}")
            if clean_indexes:
                self._subtitle.sort()

        return modified

    def finalize(self) -> None:
        self._subtitle = None
