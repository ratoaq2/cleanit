"""Make the cleanit logo, icon, and social preview card.

Run from the repository root (Python 3.11 or later, for tomllib):

    uv run --no-project --with fonttools --with resvg-py python scripts/brand.py

It writes these files to docs/images/:

- logo-light.svg, logo-dark.svg, logo-light.png, logo-dark.png: the README header (GitHub light and dark mode)
- icon.svg, icon-16.png ... icon-512.png: favicon and avatar
- social.png: the GitHub social preview. Upload it by hand: Settings, General, Social preview.

The tagline below the word mark is the `description` in pyproject.toml. The README `alt` text has the same
sentence. Change both together.

The icon is three subtitle lines. The middle line is short and ends in a sparkle: cleanit made it clean.
The palette is the same as trakit: cream lines and a gold accent on a dark tile.

All text is drawn as paths from scripts/brand/Nunito.ttf (SIL Open Font License, see scripts/brand/OFL.txt).
So the output does not depend on the fonts of the computer.

The cleanit name, logo, and icon are not covered by the Apache License 2.0 of this repository.
"""

from pathlib import Path

import resvg_py
import tomllib
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "images"
FONT = ROOT / "scripts" / "brand" / "Nunito.ttf"
TAGLINE = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["description"]

TILE, CREAM, GOLD = "#161b22", "#f5eedc", "#b07d2a"  # GOLD: contrast 3.6 on GitHub light, 5.2 on GitHub dark
TEXT = {"light": "#1f2328", "dark": "#f0f6fc"}  # GitHub text colors
GRAY = {"light": "#59636e", "dark": "#9198a1"}
GITHUB_DARK = "#0d1117"


def font(weight: int) -> TTFont:
    f = TTFont(FONT)
    return instantiateVariableFont(f, {a.axisTag: weight if a.axisTag == "wght" else None for a in f["fvar"].axes})


def text_path(f: TTFont, text: str, x_height: float, baseline: float) -> tuple[str, float]:
    """Return (d, width): text as SVG path data, from x=0. The x-height is `x_height`."""
    glyphs, cmap = f.getGlyphSet(), f.getBestCmap()
    scale = x_height / f["OS/2"].sxHeight
    pen, x = SVGPathPen(glyphs), 0.0
    for ch in text:
        glyph = glyphs[cmap[ord(ch)]]
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
        x += glyph.width * scale
    return pen.getCommands(), x


def line(x: float, y: float, w: float) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="16" rx="8" fill="{CREAM}"/>'


def icon() -> str:
    """Three subtitle lines. The middle line is short and ends in a sparkle (a star with concave sides)."""
    cx, cy, r = 66, 50, 20
    sparkle = (
        f"M{cx} {cy - r} Q{cx} {cy} {cx + r} {cy} Q{cx} {cy} {cx} {cy + r} "
        f"Q{cx} {cy} {cx - r} {cy} Q{cx} {cy} {cx} {cy - r} Z"
    )
    return (
        f'<rect x="1" y="1" width="98" height="98" rx="21" fill="{TILE}" stroke="#ffffff" stroke-opacity=".18" '
        'stroke-width="2"/>'
        + line(14, 13, 72)
        + line(14, 42, 26)
        + line(14, 71, 72)
        + f'<path d="{sparkle}" fill="{GOLD}"/>'
    )


def logo(mode: str, clean: tuple[str, float], it: tuple[str, float], tagline: tuple[str, float]) -> tuple[str, float]:
    """The icon, then 'clean' and 'it' with the tagline below. Returns (SVG body, width). The height is 100."""
    body = (
        f'<svg width="100" height="100" viewBox="0 0 100 100">{icon()}</svg>'
        f'<path transform="translate(124 0)" d="{clean[0]}" fill="{TEXT[mode]}"/>'
        f'<path transform="translate({124 + clean[1]:.1f} 0)" d="{it[0]}" fill="{GOLD}"/>'
        f'<path transform="translate(124 0)" d="{tagline[0]}" fill="{GRAY[mode]}"/>'
    )
    return body, 124 + max(clean[1] + it[1], tagline[1])


def svg(body: str, w: float, h: float) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">'
        f"{body}</svg>"
    )


def png(name: str, content: str, w: float, h: float) -> None:
    data = resvg_py.svg_to_bytes(svg_string=content, width=round(w), height=round(h), skip_system_fonts=True)
    (OUT / name).write_bytes(bytes(data))


def main() -> None:
    bold, medium = font(900), font(500)
    clean, it = text_path(bold, "clean", 36, 60), text_path(bold, "it", 36, 60)
    tagline = text_path(medium, TAGLINE, 15, 93)

    for mode in ("light", "dark"):
        body, w = logo(mode, clean, it, tagline)
        (OUT / f"logo-{mode}.svg").write_text(svg(body, w, 100) + "\n", encoding="utf-8")
        png(f"logo-{mode}.png", svg(body, w, 100), w * 4, 400)

    (OUT / "icon.svg").write_text(svg(icon(), 100, 100) + "\n", encoding="utf-8")
    for size in (16, 32, 64, 256, 512):
        png(f"icon-{size}.png", svg(icon(), 100, 100), size, size)

    body, w = logo("dark", clean, it, tagline)
    scale = 2.6
    card = (
        f'<rect width="1280" height="640" fill="{GITHUB_DARK}"/>'
        f'<g transform="translate({(1280 - w * scale) / 2:.1f} {320 - 50 * scale:.1f}) scale({scale})">{body}</g>'
    )
    png("social.png", svg(card, 1280, 640), 1280, 640)


if __name__ == "__main__":
    main()
