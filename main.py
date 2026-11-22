#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Sunday 22 November 2026.

Pure Python 3.13 standard library. Renders a 1024x1024 newspaper front
page with a hand-built 5x7 bitmap font and a hand-rolled PNG encoder, so
the output is byte-identical on every run. No network, no files read.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   (writes out/entry.png)
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (22, 22, 22)
SOFT = (74, 70, 62)
RED = (176, 42, 48)
NAVY = (20, 38, 66)
NAVY_LT = (38, 60, 96)
GOLD = (198, 152, 52)
TEAL = (15, 107, 92)
BLUE = (31, 78, 121)
PURPLE = (91, 45, 142)
BROWN = (138, 90, 43)
ORANGE = (180, 85, 31)
GREEN = (46, 107, 52)
WHITE = (255, 255, 255)
SKY = (96, 130, 170)
FLAME = (232, 116, 44)
FLAME2 = (244, 180, 60)

# ------------------------------------------------------------------- font
# 5x7 bitmap font, '#' = pixel on. Lowercase is rendered as uppercase.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "   # ", "  #  ", " #   ", "#    "),
    "%": ("#   #", "#  # ", "   # ", "  #  ", " #   ", "#  # ", "#   #"),
    "+": ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", " ### ", "     ", " ### ", "     ", "     "),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "*": ("     ", "#   #", " # # ", " ### ", " # # ", "#   #", "     "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "·": ("     ", "     ", "     ", " ##  ", " ##  ", "     ", "     "),
    "•": ("     ", "     ", "     ", " ##  ", " ##  ", "     ", "     "),
    "—": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
}
for _ch, _g in FONT.items():
    assert len(_g) == 7 and all(len(_row) == 5 for _row in _g), _ch

_REPLACEMENTS = {
    "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "‐": "-",
    "é": "e", "è": "e", "ê": "e", "á": "a", "í": "i", "ó": "o",
    "ú": "u", "ñ": "n", "ü": "u", "ç": "c",
}


def _clean(text):
    out = []
    for ch in text:
        ch = _REPLACEMENTS.get(ch, ch)
        out.append(ch.upper() if ch.isalpha() else ch)
    return "".join(out)


def text_width(text, scale):
    return len(_clean(text)) * 6 * scale


def wrap(text, max_width, scale):
    """Word-wrap cleaned text into lines fitting max_width pixels."""
    max_chars = max(1, max_width // (6 * scale))
    words = _clean(text).split(" ")
    lines, cur = [], ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bytes(bg) * (w * h))

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def hline(self, x0, x1, y, color):
        if y < 0 or y >= self.h:
            return
        x0, x1 = max(0, x0), min(self.w - 1, x1)
        if x1 < x0:
            return
        row = bytes(color) * (x1 - x0 + 1)
        i = (y * self.w + x0) * 3
        self.buf[i:i + len(row)] = row

    def vline(self, x, y0, y1, color):
        if x < 0 or x >= self.w:
            return
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            self._set(x, y, color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            self.hline(x, x + w - 1, yy, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for t in range(thick):
                self._set(x0 + t, y0, color)
                self._set(x0, y0 + t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, color, t=2):
        self.disc(cx, cy, r, color)
        self.disc(cx, cy, r - t, PAPER)

    def fill_poly(self, pts, color):
        ys = range(min(y for _, y in pts), max(y for _, y in pts) + 1)
        n = len(pts)
        for y in ys:
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, color)

    def star(self, cx, cy, r_out, r_in, spikes, color):
        pts = []
        for i in range(spikes * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.pi * i / spikes - math.pi / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.fill_poly(pts, color)

    def arc(self, cx, cy, r, a0, a1, color, thick=2):
        steps = max(8, int(abs(a1 - a0) * r / 4))
        prev = None
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            p = (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))
            if prev is not None:
                self.line(prev[0], prev[1], p[0], p[1], color, thick)
            prev = p

    # -------------------------------------------------------------- text
    def draw_text(self, x, y, text, scale, color):
        text = _clean(text)
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx - x

    def text_centered(self, y, text, scale, color):
        w = text_width(text, scale)
        self.draw_text((W - w) // 2, y, text, scale, color)

    def para(self, x, y, lines, scale, color, leading=17):
        for ln in lines:
            self.draw_text(x, y, ln, scale, color)
            y += leading
        return y


# --------------------------------------------------------------------- png
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            _chunk(b"IEND", b""))


# ------------------------------------------------------------------ layout
M = 28            # outer margin
RIGHT = W - M     # 996


def draw_masthead(cv):
    cv.text_centered(30, "THE WORLD TODAY", 6, INK)
    cv.hline(M, RIGHT - 1, 84, INK)
    cv.text_centered(92, "SUNDAY, 22 NOVEMBER 2026", 2, RED)
    cv.hline(M, RIGHT - 1, 116, INK)
    cv.hline(M, RIGHT - 1, 120, INK)


def draw_headline_graphic(cv):
    """Night sky over the Gulf: explosion burst, skyline, missile arcs."""
    x0, y0, x1, y1 = 652, 140, RIGHT, 420
    cv.rect(x0, y0, x1 - x0, y1 - y0, NAVY)
    cv.draw_text(x0 + 16, y0 + 14, "THE GULF, OVERNIGHT", 2, GOLD)
    # stars
    for sx, sy in [(680, 190), (720, 176), (940, 182), (968, 210),
                   (700, 240), (962, 250), (760, 168), (900, 168)]:
        cv.disc(sx, sy, 2, WHITE)
    # missile arcs (white trails with bright heads)
    cv.arc(700, 400, 150, -1.25, -0.35, WHITE, 3)
    cv.arc(940, 410, 170, -2.75, -1.9, WHITE, 3)
    cv.disc(800, 262, 5, WHITE)
    cv.disc(852, 258, 5, WHITE)
    # explosion burst
    cv.star(824, 300, 62, 26, 12, FLAME)
    cv.star(824, 300, 40, 17, 12, FLAME2)
    cv.disc(824, 300, 16, (255, 236, 170))
    # skyline silhouette
    base = y1
    for bx, bw, bh in [(652, 34, 46), (688, 26, 70), (716, 40, 38),
                       (758, 24, 58), (784, 36, 44), (822, 28, 66),
                       (852, 38, 40), (892, 26, 60), (920, 34, 46),
                       (956, 40, 56)]:
        cv.rect(bx, base - bh, bw, bh, (10, 20, 38))
        for wy in range(base - bh + 8, base - 6, 14):
            for wx in range(bx + 5, bx + bw - 4, 10):
                cv.rect(wx, wy, 3, 4, GOLD)
    cv.hline(x0, x1 - 1, y1 - 1, GOLD)
    cv.draw_text(x0 + 16, y1 - 24, "MISSILES OVER BAHRAIN", 2, WHITE)


def draw_headline(cv):
    cv.draw_text(M, 140, "MIDDLE EAST - GULF IN FLAMES", 2, RED)
    cv.draw_text(M, 166, "IRAN STRIKES", 5, INK)
    cv.draw_text(M, 208, "BAHRAIN", 5, INK)
    deck = wrap(
        "Tehran says its missiles and drones hit two US Patriot radars "
        "at al-Riffa and Awali. Bahrain says a civilian plant was hit "
        "and caught fire. No injuries were reported.",
        600, 2)
    y = cv.para(M, 258, deck, 2, SOFT)
    deck2 = wrap(
        "Hours later, a Houthi missile heading for western Saudi Arabia "
        "was intercepted, and Bahrain appealed to the UN Security Council.",
        600, 2)
    y = cv.para(M, y + 8, deck2, 2, SOFT)
    y += 10
    cv.hline(M, 620, y, RED)
    cv.draw_text(M, y + 8, "IRGC: IRANIAN AIRSPACE IS A RED LINE", 2, RED)


STORIES = [
    dict(kicker="GAZA", color=TEAL,
         title="FOUR NATIONS URGE ISRAEL TO OPEN GAZA TO AID",
         body="Australia, Canada, Italy and Britain call for immediate, "
              "unrestricted access as floods add to the suffering of "
              "Palestinians in Gaza."),
    dict(kicker="ISRAEL", color=BLUE,
         title="EISENKOT GETS MANDATE, INVITES LIKUD TO TALKS",
         body="President Herzog formally tasks Gadi Eisenkot with forming "
              "a government at a Sunday ceremony. Eisenkot invites "
              "Netanyahu's Likud to talks."),
    dict(kicker="HONG KONG", color=PURPLE,
         title="HONG KONG VOTES FOR ITS ELECTION COMMITTEE",
         body="856 candidates chase 723 seats as 5,709 voters choose the "
              "1,500-member body that will pick the city's next chief "
              "executive."),
    dict(kicker="MYANMAR", color=BROWN,
         title="QUAKE OF 4.1 SHAKES MYANMAR BEFORE DAWN",
         body="A magnitude 4.1 earthquake strikes Myanmar in the early "
              "hours of Sunday, India's National Centre for Seismology "
              "says."),
    dict(kicker="FRANCE", color=ORANGE,
         title="FRANCE: FOURTH WEEKEND OF COST-OF-LIVING PROTESTS",
         body="Nationwide demonstrations against the government enter a "
              "fourth straight weekend, driven by anger over rising "
              "prices."),
    dict(kicker="SPORT", color=GREEN,
         title="ALCARAZ V ZVEREV FOR THE ATP FINALS CROWN",
         body="The top two seeds meet in Turin at 6pm CET. Alcaraz beat "
              "Shelton; Zverev beat Medvedev. France beat Argentina to "
              "reach the rugby final."),
]


def draw_story(cv, x, y, w, story):
    cv.hline(x, x + w - 1, y, story["color"])
    cv.hline(x, x + w - 1, y + 2, story["color"])
    cv.draw_text(x, y + 10, story["kicker"], 2, story["color"])
    title_lines = wrap(story["title"], w, 2)
    yy = cv.para(x, y + 32, title_lines, 2, INK)
    body_lines = wrap(story["body"], w, 2)
    cv.para(x, yy + 6, body_lines, 2, SOFT)


def draw_grid(cv):
    col_w = 472
    xs = [M, 524]
    ys = [452, 616, 780]
    for i, story in enumerate(STORIES):
        draw_story(cv, xs[i % 2], ys[i // 2], col_w, story)


def draw_footer(cv):
    y = 940
    cv.draw_text(M, y, "ALSO TODAY:", 2, RED)
    items = ("US details USD 12bn in Venezuelan oil revenue - Kenya "
             "discharges its last Ebola patient - Al-Shabaab claims "
             "hundreds killed in Somalia")
    first_w = W - 2 * M - text_width("ALSO TODAY: ", 2)
    first_lines = wrap(items, first_w, 2)
    cv.draw_text(M + text_width("ALSO TODAY: ", 2), y, first_lines[0], 2, INK)
    yy = y + 17
    for ln in first_lines[1:]:
        cv.draw_text(M, yy, ln, 2, INK)
        yy += 17
    cv.hline(M, RIGHT - 1, 990, INK)
    cv.text_centered(998, "SOURCES: REUTERS - AL JAZEERA - AP - ATP TOUR - "
                          "HONG KONG GOVT", 2, SOFT)


def draw():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_headline_graphic(cv)
    draw_headline(cv)
    cv.hline(M, RIGHT - 1, 436, INK)
    draw_grid(cv)
    draw_footer(cv)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = encode_png(draw())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
