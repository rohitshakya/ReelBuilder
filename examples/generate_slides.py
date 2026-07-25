#!/usr/bin/env python3
"""Generate colorful placeholder slides for local demos."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "slides"
COLORS = [
    ((232, 67, 92), (45, 20, 30)),
    ((46, 196, 182), (15, 40, 45)),
    ((255, 159, 28), (40, 28, 10)),
    ((76, 110, 245), (18, 24, 55)),
    ((124, 255, 107), (12, 28, 18)),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 96)
        small = ImageFont.truetype("DejaVuSans.ttf", 36)
    except OSError:
        font = ImageFont.load_default()
        small = font

    for i, (fg, bg) in enumerate(COLORS, start=1):
        img = Image.new("RGB", (1080, 1350), color=bg)
        draw = ImageDraw.Draw(img)
        # Soft gradient bars
        for y in range(0, 1350, 40):
            mix = int(20 + (y / 1350) * 40)
            draw.rectangle([0, y, 1080, y + 20], fill=(bg[0], bg[1], min(255, bg[2] + mix)))
        label = f"{i:03d}"
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((1080 - tw) / 2, (1350 - th) / 2 - 40), label, fill=fg, font=font)
        sub = "ReelForge"
        sb = draw.textbbox((0, 0), sub, font=small)
        sw = sb[2] - sb[0]
        draw.text(((1080 - sw) / 2, (1350 - th) / 2 + 80), sub, fill=fg, font=small)
        path = OUT / f"{i:03d}.png"
        img.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
