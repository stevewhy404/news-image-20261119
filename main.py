#!/usr/bin/env python3
"""news-image-20261119: sum up the world news of Thursday 19 November 2026
in one image. Python stdlib only, no network, no external assets.
Deterministic: every run writes byte-identical /output/entry.png (1024x1024).
Design: a one-page newspaper front page -- masthead, lead story (GTA VI),
six more stories in a grid, each with a small drawn pictogram.
"""
import os
import struct
import zlib

W, H = 1024, 1024
OUT = "/output/entry.png"

PAPER = (247, 243, 234)
INK = (17, 17, 17)
RED = (178, 34, 34)
NAVY = (30, 58, 95)
BLUE = (29, 78, 160)
GREEN = (20, 83, 45)
TEAL = (13, 94, 94)
BLACK = (10, 10, 14)
GREY = (90, 86, 78)
ORANGE = (234, 120, 40)
PINK = (226, 110, 130)
PURPLE = (90, 60, 120)
YELLOW = (240, 200, 60)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '1' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    'q': ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}
BLANK = ("00000",) * 7


def glyph(ch):
    return FONT.get(ch, BLANK)

# ---------------------------------------------------------------- canvas
canvas = bytearray(W * H * 3)


def fill(color):
    r, g, b = color
    for i in range(0, W * H * 3, 3):
        canvas[i] = r
        canvas[i + 1] = g
        canvas[i + 2] = b


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i] = color[0]
        canvas[i + 1] = color[1]
        canvas[i + 2] = color[2]


def rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            canvas[i] = color[0]
            canvas[i + 1] = color[1]
            canvas[i + 2] = color[2]


def hline(x0, x1, y, color, t=1):
    for yy in range(y, y + t):
        for xx in range(min(x0, x1), max(x0, x1) + 1):
            px(xx, yy, color)


def vline(x, y0, y1, color, t=1):
    for xx in range(x, x + t):
        for yy in range(min(y0, y1), max(y0, y1) + 1):
            px(xx, yy, color)


def line(x0, y0, x1, y1, color):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        px(x0, y0, color)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        hline(cx - dx, cx + dx, cy + dy, color)


def ring(cx, cy, r, color, t=2):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        for k in range(t):
            px(cx - dx + k, cy + dy, color)
            px(cx + dx - k, cy + dy, color)


# ---------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale


def draw_text(s, x, y, scale, color, align="l"):
    if align == "c":
        x -= text_width(s, scale) // 2
    elif align == "r":
        x -= text_width(s, scale)
    cx = x
    for ch in s:
        g = glyph(ch)
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "1":
                    rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return x


def wrap(text, scale, maxw):
    """Greedy word wrap; returns list of lines fitting maxw pixels."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(text, x, y, scale, maxw, color, pitch=None):
    pitch = pitch or (7 * scale + 5)
    yy = y
    for ln in wrap(text, scale, maxw):
        draw_text(ln, x, yy, scale, color)
        yy += pitch
    return yy

# ---------------------------------------------------------------- pictograms
def icon_dome(x, y, w, h, color):
    # US Capitol dome: base, columns, dome arc
    cx = x + w // 2
    rect(cx - w // 2 + 6, y + h - 12, w - 12, 4, color)
    for i in range(5):
        colx = x + 10 + i * (w - 20) // 4
        vline(colx, y + h - 30, y + h - 12, color, 3)
    rect(cx - w // 2 + 6, y + h - 32, w - 12, 3, color)
    for r in range(0, 16, 2):
        dx = int((16 * 16 - r * r) ** 0.5) if r < 16 else 0
        hline(cx - dx * (w // 2 - 8) // 16, cx + dx * (w // 2 - 8) // 16,
              y + h - 32 - (16 - r), color)
    vline(cx, y + 2, y + h - 48, color, 2)


def icon_warning(x, y, w, h, color):
    cx, top, bot = x + w // 2, y + 4, y + h - 4
    line(cx, top, x + 6, bot, color)
    line(cx, top, x + w - 6, bot, color)
    hline(x + 6, x + w - 6, bot, color, 3)
    vline(cx, top + 14, top + 30, color, 4)
    disc(cx, bot - 8, 3, color)


def icon_stars(x, y, w, h, color):
    # ring of 12 stars around a coin
    cx, cy = x + w // 2, y + h // 2
    disc(cx, cy, 18, color)
    for k in range(12):
        import math
        a = k * math.pi / 6
        sx = int(cx + 30 * math.cos(a))
        sy = int(cy + 24 * math.sin(a))
        disc(sx, sy, 2, color)
    draw_text("45", cx - 12, cy - 7, 2, NAVY)


def icon_chip(x, y, w, h, color):
    cx, cy = x + w // 2, y + h // 2
    rect(cx - 16, cy - 16, 32, 32, color)
    rect(cx - 8, cy - 8, 16, 16, GREEN)
    for i in range(4):
        vline(cx - 12 + i * 8, cy - 24, cy - 16, color, 2)
        vline(cx - 12 + i * 8, cy + 16, cy + 24, color, 2)
        hline(cx - 24, cx - 16, cy - 12 + i * 8, color, 2)
        hline(cx + 16, cx + 24, cy - 12 + i * 8, color, 2)


def icon_spiral(x, y, w, h, color):
    cx, cy = x + w // 2, y + h // 2
    for r in range(4, 30, 4):
        ring(cx, cy, r, color, 2)
    disc(cx, cy, 4, color)


def icon_voyager(x, y, w, h, color):
    cx, cy = x + w // 2, y + h // 2
    for sx, sy in ((x + 8, y + 8), (x + 22, y + 26), (x + w - 10, y + 12),
                   (x + w - 24, y + 34), (x + w // 2, y + 6), (x + 12, y + h - 10)):
        disc(sx, sy, 2, color)
    line(cx - 14, cy - 8, cx + 14, cy + 8, color)
    line(cx - 14, cy + 8, cx + 14, cy - 8, color)
    disc(cx, cy, 5, color)
    line(cx + 14, cy, cx + 26, cy - 8, color)


def icon_sunset(x, y, w, h):
    # Vice City dusk: banded sky, sun, skyline, palms
    bands = [PURPLE, PINK, ORANGE, (250, 190, 90)]
    bh = h // 4
    for i, c in enumerate(bands):
        rect(x, y + i * bh, w, bh + 1, c)
    disc(x + w // 2, y + h // 2 - 10, 42, (255, 240, 180))
    # skyline
    base = y + h
    heights = [70, 110, 55, 130, 80, 100, 60, 120, 75, 95]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        rect(x + i * bw + 2, base - hh, bw - 4, hh, BLACK)
        for wy in range(base - hh + 8, base - 6, 14):
            for wx in range(x + i * bw + 6, x + (i + 1) * bw - 6, 10):
                if (wx * 7 + wy * 13) % 5 == 0:
                    rect(wx, wy, 3, 4, YELLOW)
    # palms
    for px0 in (x + 22, x + w - 28):
        line(px0, base, px0 + 4, base - 66, BLACK)
        for dx, dy in ((-18, -66), (-11, -76), (0, -78), (11, -76), (18, -66)):
            line(px0 + 4, base - 66, px0 + 4 + dx, base - 66 + dy // 3, BLACK)


# ---------------------------------------------------------------- layout
def story_cell(x, y, w, h, kicker, headline, body, band, icon):
    rect(x, y, w, 68, band)
    icon(x + 10, y + 6, 56, 56, WHITE)
    draw_text(kicker, x + 76, y + 8, 2, WHITE)
    draw_text(headline.split("|")[0], x + 76, y + 26, 2, WHITE)
    if "|" in headline:
        draw_text(headline.split("|")[1], x + 76, y + 44, 2, WHITE)
    yy = y + 78
    for ln in wrap(body, 2, w - 8):
        draw_text(ln, x + 4, yy, 2, INK)
        yy += 19
    return yy


def build():
    fill(PAPER)
    # outer double border
    rect(8, 8, W - 16, 3, INK)
    rect(8, H - 11, W - 16, 3, INK)
    rect(8, 8, 3, H - 16, INK)
    rect(W - 11, 8, 3, H - 16, INK)
    rect(16, 16, W - 32, 1, INK)
    rect(16, H - 17, W - 32, 1, INK)

    # masthead
    draw_text("THE WORLD TODAY", (W - text_width("THE WORLD TODAY", 8)) // 2, 34, 8, INK)
    hline(32, W - 32, 118, RED, 3)
    draw_text("THURSDAY 19 NOVEMBER 2026",
              (W - text_width("THURSDAY 19 NOVEMBER 2026", 3)) // 2, 130, 3, RED)
    hline(32, W - 32, 162, INK, 2)

    # ---- lead story: GTA VI
    draw_text("LEAD STORY  -  GAMES", 32, 180, 2, RED)
    para("GRAND THEFT AUTO VI", 32, 206, 4, 560, INK, pitch=36)
    para("ROLLS OUT WORLDWIDE", 32, 242, 4, 560, INK, pitch=36)
    para("After a 13-year wait, Grand Theft Auto VI began its "
         "global rollout today, sending gamers back to Vice City. "
         "Critics call it the biggest entertainment launch in "
         "history - and maybe the end of an era for gaming.",
         32, 292, 2, 556, INK, pitch=19)
    icon_sunset(620, 180, 372, 250)
    draw_text("Vice City at dusk.", 620, 438, 2, GREY)
    hline(32, W - 32, 470, INK, 2)

    # ---- also today
    draw_text("ALSO TODAY", 32, 488, 3, INK)
    hline(32, W - 32, 522, RED, 3)

    cols = (32, 360, 688)
    rows = (534, 760)
    cells = [
        ("US POLITICS", "JEFFRIES MAKES|HISTORY",
         "Democrats nominate Hakeem Jeffries for House Speaker - "
         "the first Black American to hold the post.", NAVY, icon_dome),
        ("MIDDLE EAST", "US AND IRAN|TRADE FIRE",
         "Strikes widen across the Gulf: Iran hits a US base in "
         "Kuwait and Bahrain after US hits on Qeshm Island.", RED, icon_warning),
        ("EUROPE", "EU PLANS 45BN|UKRAINE LOAN",
         "Brussels proposes a 45 billion euro loan for Kyiv, to "
         "be repaid once Russia pays reparations.", BLUE, icon_stars),
        ("TECH", "NVIDIA'S|NEW ERA",
         "After Jensen Huang's exit, acting CEO Colette Kress "
         "promises earlier pay rises; H-chip sales to China halted.",
         GREEN, icon_chip),
        ("WEATHER", "CYCLONE AKVAN|NEARS INDIA",
         "The storm is set to cross between Machilipatnam and "
         "Puri as India braces for landfall.", TEAL, icon_spiral),
        ("SPACE", "VOYAGER 1 GOES|FARTHER",
         "After nearly 50 years in space, NASA's Voyager 1 is "
         "believed to have reached one light-day from Earth.",
         BLACK, icon_voyager),
    ]
    for i, (kick, head, body, band, ic) in enumerate(cells):
        cx = cols[i % 3]
        cy = rows[i // 3]
        story_cell(cx, cy, 304, 210, kick, head, body, band, ic)

    # footer
    hline(32, W - 32, 982, INK, 1)
    draw_text("Compiled from AP, BBC, Reuters, NDTV - 19 November 2026",
              (W - text_width("Compiled from AP, BBC, Reuters, NDTV - 19 November 2026", 2)) // 2,
              990, 2, GREY)


# ---------------------------------------------------------------- PNG encode
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += canvas[yy * W * 3:(yy + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(encode_png())


if __name__ == "__main__":
    main()
