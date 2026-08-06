#!/usr/bin/env python3
"""Generate favicon + Open Graph assets matching the PBR docs theme.

Theme tokens (from docs/_sass/color_schemes/pbr.scss + custom.scss):
  accent #0f766e · ink #0b1c24 · muted #3d5560 · bg #f3f6f5 · border #c9d6d2

Usage:
  /usr/bin/python3 docs/scripts/generate-brand-assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images"
OUT.mkdir(parents=True, exist_ok=True)

ACCENT = (15, 118, 110)  # #0f766e
ACCENT_SOFT = (216, 235, 231)  # #d8ebe7
INK = (11, 28, 36)  # #0b1c24
MUTED = (61, 85, 96)  # #3d5560
BG = (243, 246, 245)  # #f3f6f5
BG_MID = (230, 238, 236)  # #e6eeec
SURFACE = (255, 255, 255)
BORDER = (201, 214, 210)  # #c9d6d2


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    return ImageFont.truetype(path, size)


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def gradient_bg(w: int, h: int) -> Image.Image:
    """Soft mint corners → near-white centre (conduit-style OG)."""
    img = Image.new("RGB", (w, h), SURFACE)
    px = img.load()
    assert px is not None
    cx, cy = w * 0.42, h * 0.45
    for y in range(h):
        for x in range(w):
            # distance from a soft focus point; corners pick up mint
            dx = (x - cx) / w
            dy = (y - cy) / h
            d = (dx * dx + dy * dy) ** 0.5
            # bottom-left mint bias
            bl = ((w - 1 - x) / w) * (y / h)
            t = min(1.0, d * 1.1 + bl * 0.35)
            px[x, y] = lerp(SURFACE, BG_MID, t * 0.55)
    return img


def rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill=None,
    outline=None,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_fork_mark(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, stroke: int) -> None:
    """Y-fork for larger diagrams (thinner rings OK at big sizes)."""
    r = int(10 * scale)
    left = (cx - int(48 * scale), cy)
    mid = (cx, cy)
    top = (cx + int(48 * scale), cy - int(28 * scale))
    bot = (cx + int(48 * scale), cy + int(28 * scale))

    draw.line([left, mid], fill=ACCENT, width=stroke)
    draw.line([mid, top], fill=ACCENT, width=stroke)
    draw.line([mid, bot], fill=ACCENT, width=stroke)

    for pt in (left, mid, top, bot):
        draw.ellipse(
            (pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r),
            fill=SURFACE,
            outline=ACCENT,
            width=max(2, stroke),
        )
    mr = int(r * 0.55)
    draw.ellipse(
        (mid[0] - mr, mid[1] - mr, mid[0] + mr, mid[1] + mr),
        fill=ACCENT,
    )


def draw_favicon_mark(draw: ImageDraw.ImageDraw, size: int, color: tuple[int, int, int]) -> None:
    """Thick solid Y-fork (OG policy / path-split) — solid nodes, fat strokes."""
    s = size
    cy = s // 2
    # ~22% stroke so the silhouette survives 16×16 downscale
    stroke = max(4, round(s * 0.22))
    r = max(3, round(s * 0.14))

    left = (round(s * 0.20), cy)
    mid = (round(s * 0.48), cy)
    top = (round(s * 0.82), round(s * 0.26))
    bot = (round(s * 0.82), round(s * 0.74))

    draw.line([left, mid], fill=color, width=stroke)
    draw.line([mid, top], fill=color, width=stroke)
    draw.line([mid, bot], fill=color, width=stroke)

    for pt in (left, mid, top, bot):
        draw.ellipse((pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r), fill=color)


def make_icon(size: int) -> Image.Image:
    """Solid teal tile + white Y-fork — high contrast in browser tabs."""
    # Draw oversized then downsample for cleaner edges at 16/32
    scale = 8 if size <= 48 else 1
    canvas = size * scale
    img = Image.new("RGB", (canvas, canvas), ACCENT)
    draw = ImageDraw.Draw(img)

    pad = max(1, canvas // 16)
    radius = max(4, canvas // 5)
    # Slightly inset rounded plate (same teal — keeps silhouette soft)
    rounded_rect(
        draw,
        (pad, pad, canvas - pad - 1, canvas - pad - 1),
        radius=radius,
        fill=ACCENT,
        outline=None,
        width=1,
    )
    draw_favicon_mark(draw, canvas, SURFACE)

    if scale > 1:
        img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def _bar(draw: ImageDraw.ImageDraw, x: int, y: int, w: int) -> None:
    draw.rounded_rectangle((x, y, x + w, y + 8), radius=4, fill=BORDER)


def _icon_spoke(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Cloud / VPC blob."""
    draw.ellipse((cx - 28, cy - 8, cx - 4, cy + 16), outline=ACCENT, width=3)
    draw.ellipse((cx - 14, cy - 18, cx + 14, cy + 10), outline=ACCENT, width=3)
    draw.ellipse((cx + 2, cy - 6, cx + 28, cy + 16), outline=ACCENT, width=3)
    draw.arc((cx - 30, cy - 4, cx + 30, cy + 22), 10, 170, fill=ACCENT, width=3)


def _icon_policy(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Shield with Y-fork decision."""
    draw.polygon(
        [
            (cx, cy - 28),
            (cx + 24, cy - 14),
            (cx + 20, cy + 18),
            (cx, cy + 28),
            (cx - 20, cy + 18),
            (cx - 24, cy - 14),
        ],
        outline=ACCENT,
        width=3,
    )
    draw.line([(cx - 10, cy), (cx, cy), (cx + 8, cy - 10)], fill=ACCENT, width=3)
    draw.line([(cx, cy), (cx + 8, cy + 10)], fill=ACCENT, width=3)
    for pt in ((cx - 10, cy), (cx, cy), (cx + 8, cy - 10), (cx + 8, cy + 10)):
        draw.ellipse((pt[0] - 3, pt[1] - 3, pt[0] + 3, pt[1] + 3), fill=ACCENT)


def _icon_paths(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Path split mark."""
    draw_fork_mark(draw, cx, cy, scale=0.55, stroke=3)


def _arrow(draw: ImageDraw.ImageDraw, x1: int, y: int, x2: int) -> None:
    draw.line([(x1, y), (x2 - 8, y)], fill=ACCENT, width=3)
    draw.polygon([(x2 - 14, y - 7), (x2, y), (x2 - 14, y + 7)], fill=ACCENT)


def make_og() -> Image.Image:
    """Prefer curated og-source.png (high-quality art); else procedural fallback."""
    source = OUT / "og-source.png"
    if source.is_file():
        img = Image.open(source).convert("RGB")
        w, h = img.size
        target_ratio = 1200 / 630
        if abs(w / h - target_ratio) > 0.02:
            if w / h > target_ratio:
                nw = int(h * target_ratio)
                x = (w - nw) // 2
                img = img.crop((x, 0, x + nw, h))
            else:
                nh = int(w / target_ratio)
                y = (h - nh) // 2
                img = img.crop((0, y, w, y + nh))
        return img.resize((1200, 630), Image.Resampling.LANCZOS)
    return make_og_procedural()


def make_og_procedural() -> Image.Image:
    """Conduit-style OG fallback: airy type left, three icon cards right."""
    w, h = 1200, 630
    img = gradient_bg(w, h)
    draw = ImageDraw.Draw(img)

    draw.text((80, 150), "AWS TRANSIT GATEWAY", font=font(22, bold=True), fill=ACCENT)
    draw.text((80, 210), "Policy-Based", font=font(64, bold=True), fill=INK)
    draw.text((80, 288), "Routing", font=font(64, bold=True), fill=INK)
    draw.text(
        (80, 400),
        "Attribute match selects the route table",
        font=font(24),
        fill=MUTED,
    )

    frame = (620, 95, 1140, 535)
    rounded_rect(draw, frame, radius=28, fill=SURFACE, outline=ACCENT, width=3)

    cards = [
        (660, 150, 790, 470, _icon_spoke),
        (830, 150, 960, 470, _icon_policy),
        (1000, 150, 1130, 470, _icon_paths),
    ]
    for x0, y0, x1, y1, icon in cards:
        rounded_rect(draw, (x0, y0, x1, y1), radius=18, fill=SURFACE, outline=ACCENT, width=2)
        cx = (x0 + x1) // 2
        icon(draw, cx, y0 + 110)
        _bar(draw, cx - 36, y0 + 200, 72)
        _bar(draw, cx - 28, y0 + 230, 56)

    mid_y = 310
    _arrow(draw, 790, mid_y, 830)
    _arrow(draw, 960, mid_y, 1000)

    return img


def save_png(img: Image.Image, name: str) -> None:
    path = OUT / name
    img.save(path, format="PNG", optimize=True)
    print(f"  wrote {path} ({img.size[0]}×{img.size[1]})")


def main() -> None:
    icon512 = make_icon(512)
    save_png(icon512, "icon-512.png")
    save_png(make_icon(180), "apple-touch-icon.png")
    save_png(make_icon(32), "favicon-32.png")
    save_png(make_icon(16), "favicon-16.png")

    # Multi-resolution ICO (16 + 32)
    ico_path = OUT / "favicon.ico"
    icon16 = make_icon(16)
    icon32 = make_icon(32)
    icon32.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32)], append_images=[icon16])
    print(f"  wrote {ico_path}")

    save_png(make_og(), "og-image.png")
    print(f"\nGenerated brand assets in {OUT}")


if __name__ == "__main__":
    main()
