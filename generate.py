#!/usr/bin/env python3
"""Draw the Sunday 22 November 2026 world-news broadsheet (entry.png).

Reads stories.json beside this file and renders a dense 1024x1024 front
page with Pillow: masthead, a lead panel with a drawn Gulf scene, seven
region blocks of story cards (each with a small drawn pictogram), a
two-column ticker of extra headlines, and a footer. Fully deterministic:
no clock, no randomness, no network.
"""

import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
MARGIN = 12

PAPER = (247, 243, 232)
INK = (26, 26, 26)
GRAY = (96, 92, 84)
RULE = (60, 56, 48)
CARD_BG = (255, 253, 247)
CARD_EDGE = (205, 198, 180)
RED = (176, 42, 30)

FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts"]


def font_path(name):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def load_font(name, size):
    return ImageFont.truetype(font_path(name), size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, font_name, start_size, min_size, max_w, max_lines):
    """Largest font size (<= start) whose wrapped text fits max_lines."""
    size = start_size
    while size >= min_size:
        f = load_font(font_name, size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines and all(
            text_w(draw, ln, f) <= max_w for ln in lines
        ):
            return f, lines
        size -= 0.5
    f = load_font(font_name, min_size)
    return f, wrap(draw, text, f, max_w)[:max_lines]


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tint(rgb, f=0.82):
    return tuple(int(c + (255 - c) * f) for c in rgb)


# ---------------------------------------------------------------- motifs
# Each painter draws inside box (x, y, s, s) using ink color `c`.

def m_missile(d, x, y, s, c):
    d.line([(x + s * .15, y + s * .85), (x + s * .55, y + s * .45)], fill=c, width=2)
    d.polygon([(x + s * .55, y + s * .30), (x + s * .72, y + s * .42),
               (x + s * .60, y + s * .55), (x + s * .45, y + s * .48)], fill=c)
    d.polygon([(x + s * .45, y + s * .60), (x + s * .38, y + s * .78),
               (x + s * .58, y + s * .68)], fill=c)
    d.ellipse([x + s * .68, y + s * .12, x + s * .86, y + s * .30], outline=c, width=2)


def m_jet(d, x, y, s, c):
    d.polygon([(x + s * .08, y + s * .55), (x + s * .55, y + s * .35),
               (x + s * .92, y + s * .45), (x + s * .60, y + s * .55),
               (x + s * .85, y + s * .78), (x + s * .62, y + s * .72),
               (x + s * .45, y + s * .62), (x + s * .25, y + s * .80)], fill=c)


def m_ship(d, x, y, s, c):
    d.polygon([(x + s * .10, y + s * .58), (x + s * .90, y + s * .58),
               (x + s * .78, y + s * .78), (x + s * .24, y + s * .78)], fill=c)
    d.rectangle([x + s * .38, y + s * .38, x + s * .62, y + s * .58], fill=c)
    d.line([(x + s * .08, y + s * .90), (x + s * .30, y + s * .84),
            (x + s * .52, y + s * .90), (x + s * .74, y + s * .84),
            (x + s * .94, y + s * .90)], fill=c, width=2)


def m_shipfire(d, x, y, s, c):
    m_ship(d, x, y + s * .12, s, c)
    for fx in (.30, .50, .68):
        d.polygon([(x + s * fx, y + s * .02), (x + s * (fx + .09), y + s * .22),
                   (x + s * (fx - .09), y + s * .22)], fill=RED)


def m_flame(d, x, y, s, c):
    d.polygon([(x + s * .50, y + s * .05), (x + s * .72, y + s * .45),
               (x + s * .80, y + s * .72), (x + s * .62, y + s * .92),
               (x + s * .36, y + s * .92), (x + s * .20, y + s * .70),
               (x + s * .30, y + s * .42)], fill=c)
    d.ellipse([x + s * .40, y + s * .55, x + s * .60, y + s * .85], fill=PAPER)


def m_globeflame(d, x, y, s, c):
    d.ellipse([x + s * .08, y + s * .22, x + s * .74, y + s * .90], outline=c, width=2)
    d.line([(x + s * .08, y + s * .56), (x + s * .74, y + s * .56)], fill=c, width=1)
    d.arc([x + s * .26, y + s * .22, x + s * .56, y + s * .90], 90, 270, fill=c, width=1)
    d.polygon([(x + s * .80, y + s * .05), (x + s * .93, y + s * .30),
               (x + s * .85, y + s * .48), (x + s * .68, y + s * .48),
               (x + s * .66, y + s * .28)], fill=RED)


def m_building(d, x, y, s, c):
    d.rectangle([x + s * .18, y + s * .18, x + s * .62, y + s * .92], fill=c)
    d.rectangle([x + s * .62, y + s * .42, x + s * .86, y + s * .92], fill=c)
    for wx in (.28, .42):
        for wy in (.30, .48, .66):
            d.rectangle([x + s * wx, y + s * wy, x + s * (wx + .08),
                         y + s * (wy + .10)], fill=PAPER)


def m_cross(d, x, y, s, c):
    d.rectangle([x + s * .40, y + s * .12, x + s * .60, y + s * .88], fill=c)
    d.rectangle([x + s * .12, y + s * .40, x + s * .88, y + s * .60], fill=c)


def m_talks(d, x, y, s, c):
    d.rectangle([x + s * .10, y + s * .18, x + s * .58, y + s * .55], outline=c, width=2)
    d.polygon([(x + s * .22, y + s * .55), (x + s * .22, y + s * .72),
               (x + s * .38, y + s * .55)], fill=c)
    d.rectangle([x + s * .44, y + s * .42, x + s * .90, y + s * .78], outline=c, width=2)
    d.polygon([(x + s * .66, y + s * .78), (x + s * .66, y + s * .94),
               (x + s * .82, y + s * .78)], fill=c)


def m_shield(d, x, y, s, c):
    d.polygon([(x + s * .50, y + s * .08), (x + s * .85, y + s * .20),
               (x + s * .82, y + s * .58), (x + s * .50, y + s * .92),
               (x + s * .18, y + s * .58), (x + s * .15, y + s * .20)], fill=c)
    d.line([(x + s * .34, y + s * .50), (x + s * .47, y + s * .64),
            (x + s * .68, y + s * .34)], fill=PAPER, width=3)


def m_gate(d, x, y, s, c):
    for gx in (.18, .38, .58, .78):
        d.line([(x + s * gx, y + s * .15), (x + s * gx, y + s * .88)], fill=c, width=3)
    d.line([(x + s * .10, y + s * .30), (x + s * .90, y + s * .30)], fill=c, width=3)
    d.line([(x + s * .10, y + s * .72), (x + s * .90, y + s * .72)], fill=c, width=3)


def m_star(d, x, y, s, c):
    pts = []
    for i in range(10):
        r = s * .44 if i % 2 == 0 else s * .18
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((x + s / 2 + r * math.cos(a), y + s / 2 + r * math.sin(a)))
    d.polygon(pts, fill=c)


def m_ballot(d, x, y, s, c):
    d.rectangle([x + s * .12, y + s * .45, x + s * .88, y + s * .90], outline=c, width=2)
    d.line([(x + s * .12, y + s * .62), (x + s * .88, y + s * .62)], fill=c, width=2)
    d.rectangle([x + s * .34, y + s * .10, x + s * .66, y + s * .45], fill=c)
    d.line([(x + s * .40, y + s * .28), (x + s * .48, y + s * .38),
            (x + s * .62, y + s * .16)], fill=PAPER, width=2)


def m_dove(d, x, y, s, c):
    d.polygon([(x + s * .10, y + s * .62), (x + s * .38, y + s * .40),
               (x + s * .62, y + s * .34), (x + s * .88, y + s * .44),
               (x + s * .64, y + s * .56), (x + s * .78, y + s * .72),
               (x + s * .46, y + s * .70), (x + s * .30, y + s * .84)], fill=c)
    d.ellipse([x + s * .70, y + s * .34, x + s * .82, y + s * .46], fill=c)


def m_target(d, x, y, s, c):
    for r in (.44, .30, .16):
        d.ellipse([x + s * (.5 - r), y + s * (.5 - r), x + s * (.5 + r),
                   y + s * (.5 + r)], outline=c, width=2)
    d.ellipse([x + s * .46, y + s * .46, x + s * .54, y + s * .54], fill=c)


def m_snow(d, x, y, s, c):
    cx, cy = x + s / 2, y + s / 2
    for k in range(6):
        a = k * math.pi / 3
        d.line([(cx - s * .4 * math.cos(a), cy - s * .4 * math.sin(a)),
                (cx + s * .4 * math.cos(a), cy + s * .4 * math.sin(a))],
               fill=c, width=2)


def m_warning(d, x, y, s, c):
    d.polygon([(x + s * .50, y + s * .10), (x + s * .90, y + s * .85),
               (x + s * .10, y + s * .85)], outline=c, width=3)
    d.line([(x + s * .50, y + s * .38), (x + s * .50, y + s * .62)], fill=c, width=3)
    d.ellipse([x + s * .46, y + s * .68, x + s * .54, y + s * .77], fill=c)


def m_bars(d, x, y, s, c):
    d.rectangle([x + s * .12, y + s * .12, x + s * .88, y + s * .88], outline=c, width=2)
    for bx in (.30, .48, .66):
        d.line([(x + s * bx, y + s * .12), (x + s * bx, y + s * .88)], fill=c, width=3)


def m_crack(d, x, y, s, c):
    d.line([(x + s * .15, y + s * .30), (x + s * .38, y + s * .30),
            (x + s * .30, y + s * .52), (x + s * .55, y + s * .52),
            (x + s * .46, y + s * .74), (x + s * .70, y + s * .74),
            (x + s * .88, y + s * .74)], fill=c, width=3)
    d.line([(x + s * .38, y + s * .30), (x + s * .50, y + s * .16)], fill=c, width=2)
    d.line([(x + s * .55, y + s * .52), (x + s * .66, y + s * .40)], fill=c, width=2)


def m_chartdown(d, x, y, s, c):
    d.line([(x + s * .14, y + s * .10), (x + s * .14, y + s * .86),
            (x + s * .90, y + s * .86)], fill=c, width=2)
    d.line([(x + s * .20, y + s * .30), (x + s * .44, y + s * .48),
            (x + s * .62, y + s * .42), (x + s * .84, y + s * .72)], fill=RED, width=3)
    d.polygon([(x + s * .84, y + s * .72), (x + s * .70, y + s * .70),
               (x + s * .80, y + s * .56)], fill=RED)


def m_virus(d, x, y, s, c):
    cx, cy = x + s / 2, y + s / 2
    for k in range(8):
        a = k * math.pi / 4
        x2, y2 = cx + s * .42 * math.cos(a), cy + s * .42 * math.sin(a)
        d.line([(cx, cy), (x2, y2)], fill=c, width=2)
        d.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=c)
    d.ellipse([cx - s * .24, cy - s * .24, cx + s * .24, cy + s * .24], fill=c)


def m_oil(d, x, y, s, c):
    d.polygon([(x + s * .50, y + s * .08), (x + s * .74, y + s * .48),
               (x + s * .72, y + s * .76), (x + s * .50, y + s * .92),
               (x + s * .28, y + s * .76), (x + s * .26, y + s * .48)], fill=c)


def m_chip(d, x, y, s, c):
    d.rectangle([x + s * .26, y + s * .26, x + s * .74, y + s * .74], outline=c, width=2)
    d.rectangle([x + s * .40, y + s * .40, x + s * .60, y + s * .60], fill=c)
    for t in (.34, .50, .66):
        d.line([(x + s * t, y + s * .10), (x + s * t, y + s * .26)], fill=c, width=2)
        d.line([(x + s * t, y + s * .74), (x + s * t, y + s * .90)], fill=c, width=2)
        d.line([(x + s * .10, y + s * t), (x + s * .26, y + s * t)], fill=c, width=2)
        d.line([(x + s * .74, y + s * t), (x + s * .90, y + s * t)], fill=c, width=2)


def m_trophy(d, x, y, s, c):
    d.polygon([(x + s * .26, y + s * .12), (x + s * .74, y + s * .12),
               (x + s * .68, y + s * .52), (x + s * .50, y + s * .64),
               (x + s * .32, y + s * .52)], fill=c)
    d.rectangle([x + s * .45, y + s * .62, x + s * .55, y + s * .78], fill=c)
    d.rectangle([x + s * .30, y + s * .78, x + s * .70, y + s * .88], fill=c)
    d.arc([x + s * .08, y + s * .16, x + s * .30, y + s * .44], 90, 270, fill=c, width=2)
    d.arc([x + s * .70, y + s * .16, x + s * .92, y + s * .44], 270, 90, fill=c, width=2)


MOTIFS = {
    "missile": m_missile, "jet": m_jet, "ship": m_ship, "shipfire": m_shipfire,
    "flame": m_flame, "globeflame": m_globeflame, "building": m_building,
    "cross": m_cross, "talks": m_talks, "shield": m_shield, "gate": m_gate,
    "star": m_star, "ballot": m_ballot, "dove": m_dove, "target": m_target,
    "snow": m_snow, "warning": m_warning, "bars": m_bars, "crack": m_crack,
    "chartdown": m_chartdown, "virus": m_virus, "oil": m_oil, "chip": m_chip,
    "trophy": m_trophy,
}


# ---------------------------------------------------------------- layout

def draw_masthead(d, data):
    name_f = load_font("DejaVuSerif-Bold.ttf", 37)
    date_f = load_font("DejaVuSans-Bold.ttf", 14)
    tag_f = load_font("DejaVuSans.ttf", 11)
    name = data["paper_name"]
    d.text(((W - text_w(d, name, name_f)) / 2, 6), name, font=name_f, fill=INK)
    date = data["date_line"]
    d.text(((W - text_w(d, date, date_f)) / 2, 50), date, font=date_f, fill=RED)
    d.line([(MARGIN, 70), (W - MARGIN, 70)], fill=RULE, width=2)
    d.line([(MARGIN, 74), (W - MARGIN, 74)], fill=RULE, width=1)


def draw_scene(d, box):
    """Drawn Gulf scene: sea, two tankers, missile arcs, coastal base."""
    x0, y0, x1, y1 = box
    sky = (203, 220, 232)
    sea = (64, 110, 150)
    d.rectangle(box, fill=sky, outline=RULE, width=1)
    sea_y = y0 + int((y1 - y0) * 0.68)
    d.rectangle([x0 + 1, sea_y, x1 - 1, y1 - 1], fill=sea)
    # sun
    d.ellipse([x1 - 52, y0 + 10, x1 - 22, y0 + 40], fill=(240, 180, 60))
    # coastal base (left): buildings + radar
    base_y = sea_y
    for bx, bw, bh in ((8, 26, 30), (38, 20, 20), (62, 30, 38)):
        d.rectangle([x0 + bx, base_y - bh, x0 + bx + bw, base_y], fill=(90, 84, 74))
    d.line([(x0 + 77, base_y - 38), (x0 + 77, base_y - 58)], fill=(90, 84, 74), width=3)
    d.arc([x0 + 62, base_y - 72, x0 + 92, base_y - 52], 200, 340, fill=(90, 84, 74), width=3)
    # explosion starburst over the base
    ex, ey = x0 + 52, base_y - 46
    for k in range(8):
        a = k * math.pi / 4
        d.line([(ex, ey), (ex + 16 * math.cos(a), ey + 16 * math.sin(a))],
               fill=(230, 90, 30), width=3)
    d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(250, 160, 40))
    # tankers
    for tx, ty, tw in ((150, 6, 120), (250, 22, 90)):
        hx, hy = x0 + tx, sea_y + ty
        d.polygon([(hx, hy), (hx + tw, hy), (hx + tw - 12, hy + 14),
                   (hx + 12, hy + 14)], fill=(40, 44, 52))
        d.rectangle([hx + tw * .55, hy - 12, hx + tw * .75, hy], fill=(120, 40, 32))
    # flames on first tanker
    fx, fy = x0 + 205, sea_y - 6
    d.polygon([(fx, fy - 22), (fx + 9, fy), (fx - 9, fy)], fill=(230, 90, 30))
    d.polygon([(fx + 14, fy - 14), (fx + 21, fy), (fx + 7, fy)], fill=(250, 160, 40))
    # missile arcs from right (Iran side) toward the base
    for (sx, sy, cx, cy) in ((330, 30, 190, -10), (300, 60, 170, 0)):
        pts = []
        for i in range(21):
            t = i / 20
            px = (1 - t) ** 2 * (x0 + sx) + 2 * (1 - t) * t * (x0 + cx) + t ** 2 * ex
            py = (1 - t) ** 2 * (y0 + sy) + 2 * (1 - t) * t * (y0 + cy) + t ** 2 * ey
            pts.append((px, py))
        d.line(pts, fill=(60, 60, 60), width=1)
        d.ellipse([x0 + sx - 3, y0 + sy - 3, x0 + sx + 3, y0 + sy + 3], fill=INK)
    # waves
    for wy in (sea_y + 26, sea_y + 40):
        pts = [(x0 + 8 + i * 14, wy + (3 if i % 2 else -3)) for i in range(28)]
        d.line(pts, fill=(150, 190, 215), width=1)
    lbl_f = load_font("DejaVuSans-Bold.ttf", 10)
    lbl = "THE GULF · STRAIT OF HORMUZ"
    d.text((x0 + 8, y1 - 16), lbl, font=lbl_f, fill=(255, 255, 255))


def draw_lead(d, lead, y0, y1):
    x0, x1 = MARGIN, W - MARGIN
    d.rectangle([x0, y0, x1, y1], fill=CARD_BG, outline=RULE, width=1)
    scene_w = 396
    draw_scene(d, (x1 - scene_w - 8, y0 + 8, x1 - 8, y1 - 8))
    tx = x0 + 12
    tw = x1 - scene_w - 20 - tx
    # kicker chip
    kick_f = load_font("DejaVuSans-Bold.ttf", 12)
    kw = text_w(d, lead["kicker"], kick_f) + 14
    d.rectangle([tx, y0 + 10, tx + kw, y0 + 30], fill=RED)
    d.text((tx + 7, y0 + 13), lead["kicker"], font=kick_f, fill=(255, 255, 255))
    # headline
    hf, hlines = fit_lines(d, lead["headline"], "DejaVuSerif-Bold.ttf",
                           26, 18, tw, 2)
    y = y0 + 36
    for ln in hlines:
        d.text((tx, y), ln, font=hf, fill=INK)
        y += hf.size + 2
    # summary
    sf, slines = fit_lines(d, lead["summary"], "DejaVuSans.ttf",
                           12, 9.5, tw, 3)
    y += 1
    for ln in slines:
        d.text((tx, y), ln, font=sf, fill=(45, 42, 38))
        y += sf.size + 2
    # bullet points
    y += 2
    for p in lead["points"]:
        pf, plines = fit_lines(d, "▸ " + p, "DejaVuSans-Bold.ttf",
                               10.5, 8.5, tw, 1)
        d.text((tx, y), plines[0], font=pf, fill=RED)
        y += pf.size + 4


def draw_story_row(d, story, x, y, w, color):
    """One 40px story row: pictogram, headline (<=2 lines), 1-line summary."""
    d.rectangle([x, y, x + w, y + 40], fill=CARD_BG)
    box = 32
    d.rectangle([x + 4, y + 4, x + 4 + box, y + 4 + box],
                fill=tint(color), outline=CARD_EDGE, width=1)
    MOTIFS[story["motif"]](d, x + 6, y + 6, box - 4, color)
    tx = x + 42
    tw = w - 48
    hf, hlines = fit_lines(d, story["headline"], "DejaVuSans-Bold.ttf",
                           12, 9, tw, 2)
    yy = y + 3
    for ln in hlines:
        d.text((tx, yy), ln, font=hf, fill=INK)
        yy += hf.size + 1.5
    sf, slines = fit_lines(d, story["summary"], "DejaVuSans.ttf",
                           9.5, 8, tw, 1)
    d.text((tx, y + 40 - sf.size - 4), slines[0], font=sf, fill=GRAY)
    d.line([(x, y + 40), (x + w, y + 40)], fill=CARD_EDGE, width=1)


def draw_region(d, region, x, y, w):
    color = hex_rgb(region["color"])
    d.rectangle([x, y, x + w, y + 17], fill=color)
    hf = load_font("DejaVuSans-Bold.ttf", 11)
    d.text((x + 6, y + 3), region["name"], font=hf, fill=(255, 255, 255))
    cnt = f"{len(region['stories'])} stories"
    d.text((x + w - text_w(d, cnt, hf) - 6, y + 3), cnt, font=hf,
           fill=(255, 255, 255))
    yy = y + 17
    for st in region["stories"]:
        draw_story_row(d, st, x, yy, w, color)
        yy += 40
    return yy


def draw_grid(d, regions, y0):
    gap = 10
    col_w = (W - 2 * MARGIN - gap) // 2
    left = [r for r in regions if r["name"] in
            ("MIDDLE EAST & GULF", "EUROPE", "AFRICA")]
    right = [r for r in regions if r not in left]
    for col, group in ((0, left), (1, right)):
        x = MARGIN + col * (col_w + gap)
        y = y0
        for region in group:
            y = draw_region(d, region, x, y, col_w) + 8


def draw_ticker(d, items, y0, y1):
    x0, x1 = MARGIN, W - MARGIN
    d.rectangle([x0, y0, x1, y1], fill=(28, 28, 30))
    hf = load_font("DejaVuSans-Bold.ttf", 11)
    d.text((x0 + 8, y0 + 3), "ALSO TODAY", font=hf, fill=(250, 200, 80))
    half = (len(items) + 1) // 2
    cols = [items[:half], items[half:]]
    col_w = (x1 - x0 - 24) // 2
    rows = max(len(c) for c in cols)
    row_h = (y1 - y0 - 20) / rows
    for ci, col in enumerate(cols):
        cx = x0 + 8 + ci * (col_w + 8)
        for ri, item in enumerate(col):
            f, lines = fit_lines(d, "▸ " + item, "DejaVuSans.ttf",
                                 10, 7.5, col_w, 1)
            d.text((cx, y0 + 19 + ri * row_h), lines[0], font=f,
                   fill=(240, 238, 230))


def draw_footer(d, data, y):
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)
    f = load_font("DejaVuSans.ttf", 10.5)
    txt = data["footer"]
    d.text(((W - text_w(d, txt, f)) / 2, y + 6), txt, font=f, fill=GRAY)


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d, data)
    draw_lead(d, data["lead"], 78, 258)
    draw_grid(d, data["regions"], 264)
    draw_ticker(d, data["ticker"], 856, 950)
    draw_footer(d, data, 958)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
