"""Generate PWA icon PNGs for kklab-flet-notes.

The script intentionally uses only the Python standard library so icons can be
regenerated after a fresh clone without extra image dependencies.
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "icons"


Color = tuple[int, int, int, int]


def rgba(hex_color: str, alpha: int = 255) -> Color:
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
        alpha,
    )


def blend(dst: Color, src: Color) -> Color:
    sr, sg, sb, sa = src
    if sa == 255:
        return src
    dr, dg, db, da = dst
    a = sa / 255
    out_a = sa + da * (1 - a)
    if out_a == 0:
        return 0, 0, 0, 0
    return (
        round((sr * sa + dr * da * (1 - a)) / out_a),
        round((sg * sa + dg * da * (1 - a)) / out_a),
        round((sb * sa + db * da * (1 - a)) / out_a),
        round(out_a),
    )


class Canvas:
    def __init__(self, size: int, bg: Color):
        self.size = size
        self.pixels = [bg] * (size * size)

    def put(self, x: int, y: int, color: Color) -> None:
        if 0 <= x < self.size and 0 <= y < self.size:
            idx = y * self.size + x
            self.pixels[idx] = blend(self.pixels[idx], color)

    def rounded_rect(
        self, x0: int, y0: int, x1: int, y1: int, radius: int, color: Color
    ) -> None:
        for y in range(y0, y1):
            for x in range(x0, x1):
                cx = min(max(x, x0 + radius), x1 - radius - 1)
                cy = min(max(y, y0 + radius), y1 - radius - 1)
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius**2:
                    self.put(x, y, color)

    def rect(self, x0: int, y0: int, x1: int, y1: int, color: Color) -> None:
        for y in range(y0, y1):
            for x in range(x0, x1):
                self.put(x, y, color)

    def circle(self, cx: int, cy: int, radius: int, color: Color) -> None:
        r2 = radius * radius
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                    self.put(x, y, color)


def downsample(source: Canvas, target_size: int) -> list[Color]:
    scale = source.size // target_size
    out: list[Color] = []
    area = scale * scale
    for y in range(target_size):
        for x in range(target_size):
            rs = gs = bs = aas = 0
            for yy in range(y * scale, (y + 1) * scale):
                row = yy * source.size
                for xx in range(x * scale, (x + 1) * scale):
                    r, g, b, a = source.pixels[row + xx]
                    rs += r
                    gs += g
                    bs += b
                    aas += a
            out.append((rs // area, gs // area, bs // area, aas // area))
    return out


def write_png(path: Path, size: int, pixels: list[Color]) -> None:
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        row = pixels[y * size : (y + 1) * size]
        for r, g, b, a in row:
            raw.extend((r, g, b, a))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def draw_icon(size: int, maskable: bool) -> list[Color]:
    scale = 4
    s = size * scale
    c = Canvas(s, rgba("#F6F8FA"))

    def v(n: float) -> int:
        return round(n * scale)

    pad = 42 if maskable else 18
    c.rounded_rect(v(pad), v(pad), v(size - pad), v(size - pad), v(42), rgba("#7FAED4"))
    c.rounded_rect(
        v(pad + 12),
        v(pad + 12),
        v(size - pad - 12),
        v(size - pad - 12),
        v(32),
        rgba("#A9CBE8", 150),
    )

    # Note page.
    page_x0 = v(size * 0.29)
    page_y0 = v(size * 0.20)
    page_x1 = v(size * 0.72)
    page_y1 = v(size * 0.77)
    c.rounded_rect(page_x0, page_y0, page_x1, page_y1, v(13), rgba("#FFFFFF"))
    c.rounded_rect(page_x0, page_y0, page_x1, page_y1, v(13), rgba("#FFFFFF", 235))

    # Folded corner.
    fold = v(size * 0.115)
    for y in range(page_y0, page_y0 + fold):
        for x in range(page_x1 - fold, page_x1):
            if x - (page_x1 - fold) + y - page_y0 >= fold:
                c.put(x, y, rgba("#DCEAF5"))

    # Lines.
    line_x0 = v(size * 0.36)
    line_x1 = v(size * 0.64)
    for i, y in enumerate([0.36, 0.46, 0.56]):
        width = line_x1 if i < 2 else v(size * 0.58)
        c.rounded_rect(line_x0, v(size * y), width, v(size * y + 0.022), v(3), rgba("#7FAED4"))

    # Tag chips.
    chips = [
        (0.34, 0.64, 0.48, "#E7A84B"),
        (0.50, 0.64, 0.66, "#70AD7E"),
    ]
    for x0, y0, x1, color in chips:
        c.rounded_rect(v(size * x0), v(size * y0), v(size * x1), v(size * (y0 + 0.055)), v(8), rgba(color))

    # Small pencil accent.
    angle = -math.pi / 4
    px = v(size * 0.63)
    py = v(size * 0.72)
    length = v(size * 0.18)
    width = v(size * 0.045)
    for t in range(length):
        cx = round(px + math.cos(angle) * t)
        cy = round(py + math.sin(angle) * t)
        c.circle(cx, cy, width // 2, rgba("#D9717D"))
    c.circle(v(size * 0.74), v(size * 0.61), v(size * 0.020), rgba("#FFFFFF"))

    return downsample(c, size)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("icon-maskable-192.png", 192, True),
        ("icon-maskable-512.png", 512, True),
    ]
    for filename, size, maskable in outputs:
        write_png(OUT_DIR / filename, size, draw_icon(size, maskable))


if __name__ == "__main__":
    main()
