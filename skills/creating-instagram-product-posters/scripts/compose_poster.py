#!/usr/bin/env python3
"""Compose licensed Korean typography over a text-free poster image."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


SKILL_DIR = Path(__file__).resolve().parents[1]
FONT_DIR = SKILL_DIR / "assets" / "fonts"
APPROVED_FONTS = {
    "Pretendard-Bold.otf": "Pretendard-OFL.txt",
    "Pretendard-Regular.otf": "Pretendard-OFL.txt",
    "NotoSansKR-Bold.otf": "NotoSansKR-OFL.txt",
    "NotoSansKR-Regular.otf": "NotoSansKR-OFL.txt",
}
CANVAS = (1080, 1350)


def validate_font(font_path: Path) -> Path:
    resolved = Path(font_path).expanduser().resolve()
    try:
        resolved.relative_to(FONT_DIR.resolve())
    except ValueError as exc:
        raise ValueError("Typography requires an approved bundled font") from exc

    license_name = APPROVED_FONTS.get(resolved.name)
    if not license_name or not resolved.is_file():
        raise ValueError("Typography requires an approved bundled font")
    if not (FONT_DIR / license_name).is_file():
        raise ValueError(f"Missing bundled font license: {license_name}")
    return resolved


def _edge_scrim(size: tuple[int, int], placement: str) -> Image.Image:
    width, height = size
    alpha = Image.new("L", size, 0)
    pixels = alpha.load()
    fade_end = int(height * 0.48)
    for offset in range(fade_end):
        opacity = int(150 * (1 - offset / fade_end) ** 1.8)
        y = offset if placement == "top" else height - 1 - offset
        for x in range(width):
            pixels[x, y] = opacity
    scrim = Image.new("RGBA", size, (5, 32, 29, 0))
    scrim.putalpha(alpha)
    return scrim


def compose_poster(
    *,
    background_path: Path,
    output_path: Path,
    title: str,
    subtitle: str,
    title_font_path: Path,
    subtitle_font_path: Path,
    subtitle_size: int = 34,
    title_spacing: int = 10,
    text_color: str = "#F7F4ED",
    placement: str = "top",
    eyebrow: str = "",
    feature_text: str = "",
    footer: str = "",
) -> Path:
    if placement not in {"top", "bottom"}:
        raise ValueError("placement must be 'top' or 'bottom'")
    title_font_path = validate_font(title_font_path)
    subtitle_font_path = validate_font(subtitle_font_path)

    with Image.open(background_path) as source:
        poster = ImageOps.fit(source.convert("RGB"), CANVAS, method=Image.Resampling.LANCZOS)

    poster = poster.convert("RGBA")
    poster.alpha_composite(_edge_scrim(CANVAS, placement))
    draw = ImageDraw.Draw(poster)
    title_font = ImageFont.truetype(str(title_font_path), 118)
    subtitle_font = ImageFont.truetype(str(subtitle_font_path), subtitle_size)
    eyebrow_font = ImageFont.truetype(str(subtitle_font_path), 24)
    detail_font = ImageFont.truetype(str(subtitle_font_path), 22)

    left = 72
    top = 82 if placement == "top" else 884
    rule_y = 48 if placement == "top" else 850
    draw.rounded_rectangle((left, rule_y, left + 54, rule_y + 8), radius=4, fill=text_color)
    draw.multiline_text(
        (left, top),
        title,
        font=title_font,
        fill=text_color,
        spacing=title_spacing,
        stroke_width=0,
    )
    title_box = draw.multiline_textbbox((left, top), title, font=title_font, spacing=title_spacing)
    subtitle_y = title_box[3] + 30
    draw.text((left + 3, subtitle_y), subtitle, font=subtitle_font, fill=text_color)
    if eyebrow:
        draw.text((left, 66), eyebrow, font=eyebrow_font, fill=text_color)
    if feature_text:
        draw.text((left + 3, subtitle_y + 62), feature_text, font=detail_font, fill=text_color)
    if footer:
        footer_box = draw.textbbox((0, 0), footer, font=detail_font)
        footer_y = CANVAS[1] - 58
        draw.text((left, footer_y), footer, font=detail_font, fill=text_color)
        draw.line((left + footer_box[2] + 18, footer_y + 12, CANVAS[0] - 72, footer_y + 12), fill=text_color, width=2)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    poster.convert("RGB").save(output_path, quality=95)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--background", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", required=True, help="Use a literal newline to control line breaks")
    parser.add_argument("--subtitle", required=True)
    parser.add_argument("--title-font", type=Path, default=FONT_DIR / "Pretendard-Bold.otf")
    parser.add_argument("--subtitle-font", type=Path, default=FONT_DIR / "Pretendard-Regular.otf")
    parser.add_argument("--subtitle-size", type=int, default=34)
    parser.add_argument("--title-spacing", type=int, default=10)
    parser.add_argument("--text-color", default="#F7F4ED")
    parser.add_argument("--placement", choices=("top", "bottom"), default="top")
    parser.add_argument("--eyebrow", default="")
    parser.add_argument("--feature-text", default="")
    parser.add_argument("--footer", default="")
    args = parser.parse_args()

    compose_poster(
        background_path=args.background,
        output_path=args.output,
        title=args.title,
        subtitle=args.subtitle,
        title_font_path=args.title_font,
        subtitle_font_path=args.subtitle_font,
        subtitle_size=args.subtitle_size,
        title_spacing=args.title_spacing,
        text_color=args.text_color,
        placement=args.placement,
        eyebrow=args.eyebrow,
        feature_text=args.feature_text,
        footer=args.footer,
    )


if __name__ == "__main__":
    main()
