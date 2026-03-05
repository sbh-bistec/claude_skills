"""
preview_day01.py
----------------
Canvas-design quality PNG for Day 1 Facebook post.
Design: Editorial bold split — dominant type left, systematic tiles right.
Fonts: Bahnschrift (geometric DIN display) + Georgia (serif) + Segoe UI.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_PATH = Path("output/preview_day01_facebook.png")
W, H     = 1200, 630

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path("C:/Windows/Fonts")

def f(name: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FONT_DIR / name), size)
    except (IOError, OSError):
        return ImageFont.load_default()


def wh(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, fnt)
    return bb[2] - bb[0], bb[3] - bb[1]


def cx(draw, y, text, fnt, fill, within_w=W, offset_x=0):
    w, _ = wh(draw, text, fnt)
    draw.text((offset_x + (within_w - w) // 2, y), text, font=fnt, fill=fill)


# ── Palette ───────────────────────────────────────────────────────────────────

PAPER = (248, 246, 240)
DARK  = (  7,  22, 20)
TEAL  = ( 14, 148, 145)
INK   = ( 12,  16, 22)
DIM   = ( 95, 100, 108)
WHITE = (255, 255, 255)

OPT_ACC = [
    ( 14, 148, 145),   # A teal
    ( 60,  90, 205),   # B indigo
    (140,  55, 190),   # C plum
    (205, 130,  18),   # D amber
]

# ── Canvas ────────────────────────────────────────────────────────────────────

img  = Image.new("RGB", (W, H), PAPER)
draw = ImageDraw.Draw(img)

SPLIT = 540

# ── Right dark panel ──────────────────────────────────────────────────────────

draw.rectangle([SPLIT, 0, W, H], fill=DARK)

# Ghost "01" in right panel — barely visible, adds depth
f_ghost = f("bahnschrift.ttf", 310)
gw, gh  = wh(draw, "01", f_ghost)
ghost_c = (12, 36, 33)
draw.text((SPLIT + (W - SPLIT - gw) // 2, (H - gh) // 2 - 15),
          "01", font=f_ghost, fill=ghost_c)

# 4 stacked option tiles
TILE_W = 450
TILE_H = 98
TILE_G = 10
tile_x = SPLIT + (W - SPLIT - TILE_W) // 2
tiles_h = 4 * TILE_H + 3 * TILE_G
tile_y  = (H - tiles_h) // 2

f_letter = f("bahnschrift.ttf", 36)
f_opt    = f("segoeuib.ttf",    19)

opts = [
    ("A", "PATIENT APPOINTMENTS"),
    ("B", "BILLING & PAYMENTS"),
    ("C", "PATIENT RECORDS"),
    ("D", "STAFF COORDINATION"),
]

for i, (letter, name) in enumerate(opts):
    acc  = OPT_ACC[i]
    ty0  = tile_y + i * (TILE_H + TILE_G)
    ty1  = ty0 + TILE_H
    tbg  = tuple(min(255, v + 16) for v in DARK)

    draw.rounded_rectangle([tile_x, ty0, tile_x + TILE_W, ty1],
                            radius=6, fill=tbg)
    # Left accent strip
    draw.rounded_rectangle([tile_x, ty0, tile_x + 5, ty1],
                            radius=3, fill=acc)
    # Circle badge
    BR = 20
    bx = tile_x + 40
    by = ty0 + TILE_H // 2
    draw.ellipse([bx - BR, by - BR, bx + BR, by + BR], fill=acc)
    lw, lh = wh(draw, letter, f_letter)
    draw.text((bx - lw // 2, by - lh // 2 - 1), letter, font=f_letter, fill=WHITE)
    # Option name
    nw, nh = wh(draw, name, f_opt)
    draw.text((tile_x + 76, ty0 + (TILE_H - nh) // 2), name, font=f_opt, fill=WHITE)
    # Bottom thin accent
    draw.rectangle([tile_x + TILE_W - 60, ty1 - 3,
                    tile_x + TILE_W - 4,  ty1 - 1], fill=acc)

# Brand name bottom-right
f_brand = f("segoeui.ttf", 16)
bw, bh  = wh(draw, "ClinicSmart SL", f_brand)
draw.text((W - 46 - bw, H - 34), "ClinicSmart SL", font=f_brand, fill=(75, 100, 97))

# ── Left editorial panel ──────────────────────────────────────────────────────

ML = 54   # left margin

# Very subtle dot-grid texture
for y in range(18, H, 28):
    for x in range(ML + 6, SPLIT - 22, 28):
        draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(228, 224, 215))

# 5-px teal accent strip (left edge)
draw.rectangle([0, 0, 5, H], fill=TEAL)


# ── Giant headline — Bahnschrift, fills left panel ────────────────────────────

f_gs = f("georgiab.ttf", 28)   # sub-serif

# Auto-size headline to fit longest word within left panel content width
MAX_TXT_W = SPLIT - ML - 20
lines_raw = ["WHAT IS", "YOUR", "CHALLENGE?"]
sz = 118
while sz > 40:
    probe = f("bahnschrift.ttf", sz)
    if max(wh(draw, t, probe)[0] for t in lines_raw) <= MAX_TXT_W:
        break
    sz -= 2
f_h = f("bahnschrift.ttf", sz)

lines = [
    ("WHAT IS",    INK),
    ("YOUR",       INK),
    ("CHALLENGE?", TEAL),
]

lh_list = [wh(draw, t, f_h)[1] for t, _ in lines]
HL_GAP  = 2
HL_H    = sum(lh_list) + HL_GAP * (len(lines) - 1)

sub       = "Running a clinic in Sri Lanka"
_, sub_h  = wh(draw, sub, f_gs)
SUB_GAP   = 22

BLOCK_H   = HL_H + SUB_GAP + sub_h
block_top = (H - BLOCK_H) // 2 - 12

cy = block_top
for (txt, clr), lh in zip(lines, lh_list):
    draw.text((ML, cy), txt, font=f_h, fill=clr)
    cy += lh + HL_GAP

# Accent rule
rule_y = cy + 14
draw.rectangle([ML, rule_y, ML + 72, rule_y + 3], fill=TEAL)

# Sub-text
draw.text((ML, rule_y + SUB_GAP - 2), sub, font=f_gs, fill=DIM)

# Hashtag bottom-left
f_hash = f("segoeuib.ttf", 16)
draw.text((ML, H - 34), "#SriLankaHealthcare", font=f_hash, fill=TEAL)

# Vertical divider
draw.line([(SPLIT, 0), (SPLIT, H)], fill=(28, 48, 46), width=1)

# ── Save ─────────────────────────────────────────────────────────────────────

img.save(str(OUT_PATH), "PNG")
print(f"Saved: {OUT_PATH}")
