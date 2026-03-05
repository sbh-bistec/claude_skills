"""
generate_posts.py
-----------------
Multi-template social media post generator for ClinicSmart SL.
10 distinct visual templates dispatched by post type/pillar.
Output: output/linkedin/, output/facebook/, output/instagram/

Fonts: Windows system fonts only (canvas-design fonts incompatible with Pillow).
"""

import json, re, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Output dirs ───────────────────────────────────────────────────────────────
for p in ["output/linkedin", "output/facebook", "output/instagram"]:
    Path(p).mkdir(parents=True, exist_ok=True)

# ── Fonts ─────────────────────────────────────────────────────────────────────
FD = Path("C:/Windows/Fonts")

def f(name: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FD / name), size)
    except Exception:
        return ImageFont.load_default()

# ── Palette ───────────────────────────────────────────────────────────────────
PAPER  = (248, 246, 240)
DARK   = (  7,  22,  20)
TEAL   = ( 14, 148, 145)
INK    = ( 12,  16,  22)
DIM    = ( 95, 100, 108)
WHITE  = (255, 255, 255)
CREAM  = (238, 234, 224)

PILLAR = {
    "Educational":       ( 14, 148, 145),
    "Before & After":    ( 60,  78, 200),
    "Social Proof":      (109,  63, 192),
    "Engagement":        (192, 122,  10),
    "Promotional":       (184,  48,  37),
    "Behind the Scenes": ( 46, 125,  82),
}

def pillar_accent(pillar: str):
    for k, v in PILLAR.items():
        if k.lower() in pillar.lower():
            return v
    return TEAL

OPT_ACC = [
    ( 14, 148, 145),
    ( 60,  90, 205),
    (140,  55, 190),
    (205, 130,  18),
]

SIZES = {
    "linkedin":  (1200, 627),
    "facebook":  (1200, 630),
    "instagram": (1080, 1080),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
emoji_re = re.compile(
    u"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
    u"\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
    u"\U00002702-\U000027B0\U000024C2-\U0001F251"
    u"\U0001f926-\U0001f937\U00010000-\U0010ffff"
    u"\u2640-\u2642\u2600-\u2B55\u200d\u23cf\u23e9"
    u"\u231a\ufe0f\u3030]+",
    flags=re.UNICODE
)

def clean(text: str) -> str:
    text = emoji_re.sub("", text)
    text = "".join(c for c in text if c.isprintable() or c == "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def wh(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, fnt)
    return bb[2] - bb[0], bb[3] - bb[1]

def wrap_px(draw, text: str, fnt, max_px: int) -> list:
    lines = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        line = []
        for word in words:
            test = " ".join(line + [word])
            if wh(draw, test, fnt)[0] > max_px and line:
                lines.append(" ".join(line))
                line = [word]
            else:
                line.append(word)
        if line:
            lines.append(" ".join(line))
    return lines or [""]

def dot_texture(draw, x0, y0, x1, y1, gap=28, clr=(228, 224, 215)):
    for y in range(y0 + 18, y1, gap):
        for x in range(x0 + 6, x1 - 6, gap):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=clr)

def accent_bar_left(draw, H, clr):
    draw.rectangle([0, 0, 5, H], fill=clr)

def brand_stamp(draw, W, H, clr=(75, 100, 97)):
    fnt = f("segoeui.ttf", 16)
    label = "ClinicSmart SL"
    lw, _ = wh(draw, label, fnt)
    draw.text((W - 46 - lw, H - 34), label, font=fnt, fill=clr)

def hashtag_stamp(draw, H, tag: str, x: int, clr=TEAL):
    fnt = f("segoeuib.ttf", 16)
    draw.text((x, H - 34), tag, font=fnt, fill=clr)

def divider_line(draw, x, H, clr=(28, 48, 46)):
    draw.line([(x, 0), (x, H)], fill=clr, width=1)

# ── Template dispatcher ───────────────────────────────────────────────────────

def detect_template(post: dict) -> str:
    t   = post.get("type", "").lower()
    p   = post.get("pillar", "").lower()
    txt = (post.get("post", "") + " " + post.get("hook", "")).lower()

    if any(k in t for k in ("holiday", "avurudu", "new year", "easter", "good friday", "community")):
        return "HOLIDAY"
    if "carousel" in t or "reel" in t:
        return "CAROUSEL"
    if "poll" in t or "engagement graphic" in t:
        return "POLL"
    if "before" in t and "after" in t:
        return "BEFORE_AFTER"
    if "quote card" in t or "testimonial" in t:
        return "QUOTE"
    if "insight" in t or "data post" in t:
        return "STATS"
    if "list post" in t or "5 things" in txt:
        return "LIST"
    if "tip" in t and ("clinic tip" in txt or "did you know" in txt):
        return "TIP"
    if "debate" in t or "discussion" in t or "hot take" in txt:
        return "DEBATE"
    if "behind" in t or "behind the scenes" in p:
        return "BTS"
    return "HOOK"

# ── Template: POLL ────────────────────────────────────────────────────────────

def extract_options(post_text: str):
    opts = []
    for line in post_text.split("\n"):
        m = re.match(r"^[A-D][):\.]?\s*(.+)", line.strip())
        if m:
            opts.append(m.group(1).strip())
    return opts[:4]

def tpl_poll(post: dict, W: int, H: int) -> Image.Image:
    acc  = pillar_accent(post.get("pillar", ""))
    img  = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    SPLIT = int(W * 0.46)
    draw.rectangle([SPLIT, 0, W, H], fill=DARK)

    day_str = f"0{post['day']}" if post['day'] < 10 else str(post['day'])
    f_ghost = f("bahnschrift.ttf", int(H * 0.55))
    gw, gh  = wh(draw, day_str, f_ghost)
    draw.text((SPLIT + (W - SPLIT - gw) // 2, (H - gh) // 2 - int(H * 0.02)),
              day_str, font=f_ghost, fill=(12, 36, 33))

    opts_raw = extract_options(post.get("post", ""))
    opts = [(chr(65 + i), opts_raw[i] if i < len(opts_raw) else f"Option {chr(65+i)}")
            for i in range(4)]
    if not opts_raw:
        opts = [("A", "PATIENT APPOINTMENTS"), ("B", "BILLING & PAYMENTS"),
                ("C", "PATIENT RECORDS"),      ("D", "STAFF COORDINATION")]

    margin_r = int(W * 0.025)
    TILE_W = W - SPLIT - 2 * margin_r
    TILE_H = max(int(H * 0.155), 72)
    TILE_G = int(H * 0.016)
    tile_x = SPLIT + margin_r
    tiles_h = 4 * TILE_H + 3 * TILE_G
    tile_y  = (H - tiles_h) // 2

    f_letter = f("bahnschrift.ttf", int(TILE_H * 0.38))
    f_opt    = f("segoeuib.ttf",    max(14, int(TILE_H * 0.19)))

    for i, (letter, name) in enumerate(opts):
        tile_acc = OPT_ACC[i]
        ty0 = tile_y + i * (TILE_H + TILE_G)
        ty1 = ty0 + TILE_H
        tbg = tuple(min(255, v + 16) for v in DARK)
        draw.rounded_rectangle([tile_x, ty0, tile_x + TILE_W, ty1], radius=6, fill=tbg)
        draw.rounded_rectangle([tile_x, ty0, tile_x + 5,      ty1], radius=3, fill=tile_acc)
        BR = int(TILE_H * 0.21)
        bx = tile_x + int(TILE_H * 0.43)
        by = ty0 + TILE_H // 2
        draw.ellipse([bx - BR, by - BR, bx + BR, by + BR], fill=tile_acc)
        lw, lh = wh(draw, letter, f_letter)
        draw.text((bx - lw // 2, by - lh // 2 - 1), letter, font=f_letter, fill=WHITE)
        max_name_w = TILE_W - int(TILE_H * 0.43) - BR - 20
        while wh(draw, name, f_opt)[0] > max_name_w and len(name) > 6:
            name = name[:-4] + "..."
        _, nh = wh(draw, name, f_opt)
        draw.text((bx + BR + 14, ty0 + (TILE_H - nh) // 2), name, font=f_opt, fill=WHITE)
        draw.rectangle([tile_x + TILE_W - 52, ty1 - 3,
                        tile_x + TILE_W - 4,  ty1 - 1], fill=tile_acc)

    brand_stamp(draw, W, H)

    ML = int(W * 0.046)
    dot_texture(draw, ML, 0, SPLIT - 20, H)
    accent_bar_left(draw, H, acc)

    # Find the question line
    hook = ""
    for line in post.get("post", "").split("\n"):
        lc = clean(line)
        if "?" in lc and len(lc) > 20:
            hook = lc
            break
    if not hook:
        hook = clean(post.get("post", "").split("\n")[0]) or "What is your biggest challenge?"

    MAX_TXT_W = SPLIT - ML - 24
    fnt_q = f("bahnschrift.ttf", 40)
    for sz in range(72, 18, -2):
        fnt_q = f("bahnschrift.ttf", sz)
        wrapped = wrap_px(draw, hook, fnt_q, MAX_TXT_W)
        lh = wh(draw, "Ag", fnt_q)[1]
        if lh * len(wrapped) + 4 * (len(wrapped) - 1) <= H * 0.52:
            break

    lh_q = wh(draw, "Ag", fnt_q)[1]
    block_h = lh_q * len(wrapped) + 4 * max(0, len(wrapped) - 1)

    f_sub = f("georgiab.ttf", max(18, int(H * 0.042)))
    sub_lh = wh(draw, "Ag", f_sub)[1]
    cy = (H - block_h - 28 - sub_lh * 2) // 2 - int(H * 0.03)

    for line in wrapped:
        clr = acc if line == wrapped[-1] else INK
        draw.text((ML, cy), line, font=fnt_q, fill=clr)
        cy += lh_q + 4

    rule_y = cy + 12
    draw.rectangle([ML, rule_y, ML + 64, rule_y + 3], fill=acc)
    cy = rule_y + 22
    draw.text((ML, cy), "YOUR CLINIC,", font=f_sub, fill=DIM)
    cy += sub_lh + 4
    draw.text((ML, cy), "YOUR CHOICE",  font=f_sub, fill=INK)

    tag = (post.get("hashtags") or ["#SriLankaHealthcare"])[0]
    hashtag_stamp(draw, H, clean(tag), ML)
    divider_line(draw, SPLIT, H)
    return img

# ── Template: HOOK ────────────────────────────────────────────────────────────

def tpl_hook(post: dict, W: int, H: int) -> Image.Image:
    acc  = pillar_accent(post.get("pillar", ""))
    img  = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    SPLIT = int(W * 0.62)
    draw.rectangle([SPLIT, 0, W, H], fill=DARK)

    ML = int(W * 0.046)
    dot_texture(draw, ML, 0, SPLIT - 20, H)
    accent_bar_left(draw, H, acc)

    hook = clean(post.get("hook", "") or post.get("post", "").split("\n")[0])
    hook = re.sub(r"^[•\-\u2013\u2014*]+\s*", "", hook)

    MAX_TXT_W = SPLIT - ML - 32
    fnt_h = f("bahnschrift.ttf", 40)
    for sz in range(96, 24, -2):
        fnt_h = f("bahnschrift.ttf", sz)
        wrapped = wrap_px(draw, hook, fnt_h, MAX_TXT_W)
        lh = wh(draw, "Ag", fnt_h)[1]
        if lh * len(wrapped) + 6 * (len(wrapped) - 1) <= H * 0.55 and len(wrapped) <= 5:
            break

    lh = wh(draw, "Ag", fnt_h)[1]
    lines_h = lh * len(wrapped) + 6 * (len(wrapped) - 1)

    body  = clean(post.get("post", ""))
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    sub   = re.sub(r"\n", " ", paras[0])[:180] if paras else ""

    f_sub = f("segoeui.ttf", max(15, int(H * 0.028)))
    sub_w = wrap_px(draw, sub, f_sub, MAX_TXT_W)
    sub_lh = wh(draw, "Ag", f_sub)[1]
    sub_h  = sub_lh * len(sub_w) + 4 * (len(sub_w) - 1)

    cy = (H - lines_h - 28 - sub_h) // 2 - int(H * 0.04)

    for i, line in enumerate(wrapped):
        clr = acc if i == len(wrapped) - 1 else INK
        draw.text((ML, cy), line, font=fnt_h, fill=clr)
        cy += lh + 6

    rule_y = cy + 12
    draw.rectangle([ML, rule_y, ML + 64, rule_y + 3], fill=acc)
    cy = rule_y + 18

    for line in sub_w:
        if line:
            draw.text((ML, cy), line, font=f_sub, fill=DIM)
        cy += sub_lh + 4

    tag = (post.get("hashtags") or ["#SriLankaHealthcare"])[0]
    hashtag_stamp(draw, H, clean(tag), ML)

    # Right panel
    day_str = f"0{post['day']}" if post['day'] < 10 else str(post['day'])
    f_ghost = f("bahnschrift.ttf", int(H * 0.52))
    gw, gh  = wh(draw, day_str, f_ghost)
    draw.text((SPLIT + (W - SPLIT - gw) // 2, (H - gh) // 2),
              day_str, font=f_ghost, fill=(12, 36, 33))

    pillar_name = post.get("pillar", "Educational").upper()
    f_label = f("segoeuib.ttf", max(12, int(H * 0.022)))
    plw, plh = wh(draw, pillar_name, f_label)
    px = SPLIT + (W - SPLIT - plw) // 2
    py = H // 2 + int(H * 0.19)
    draw.rounded_rectangle([px - 8, py - 4, px + plw + 8, py + plh + 4], radius=4, fill=acc)
    draw.text((px, py), pillar_name, font=f_label, fill=WHITE)

    brand_stamp(draw, W, H)
    divider_line(draw, SPLIT, H)
    return img

# ── Template: BEFORE/AFTER ────────────────────────────────────────────────────

def extract_before_after(post_text: str):
    before, after = [], []
    mode = None
    for line in post_text.split("\n"):
        ls = clean(line).strip()
        if not ls:
            continue
        if re.search(r"\bBEFORE\b", ls, re.I):
            mode = "before"
        elif re.search(r"\bAFTER\b", ls, re.I):
            mode = "after"
        elif mode == "before" and re.match(r"^[Xx\u274c\u2718\u2717\-]", ls):
            before.append(re.sub(r"^[Xx\u274c\u2718\u2717\-\u2013]+\s*", "", ls))
        elif mode == "after" and re.match(r"^[\u2705Vv\+]", ls):
            after.append(re.sub(r"^[\u2705Vv\+]+\s*", "", ls))
    return before[:4], after[:4]

def tpl_before_after(post: dict, W: int, H: int) -> Image.Image:
    SPLIT = W // 2
    img   = Image.new("RGB", (W, H), DARK)
    draw  = ImageDraw.Draw(img)

    draw.rectangle([0, 0, SPLIT, H], fill=(40, 10, 10))
    draw.rectangle([SPLIT, 0, W, H], fill=(5, 25, 24))
    draw.rectangle([SPLIT - 2, 0, SPLIT + 2, H], fill=WHITE)

    f_vs = f("bahnschrift.ttf", int(H * 0.07))
    vsw, vsh = wh(draw, "VS", f_vs)
    draw.rounded_rectangle([SPLIT - vsw // 2 - 10, H // 2 - vsh // 2 - 8,
                             SPLIT + vsw // 2 + 10, H // 2 + vsh // 2 + 8],
                            radius=6, fill=WHITE)
    draw.text((SPLIT - vsw // 2, H // 2 - vsh // 2), "VS", font=f_vs, fill=INK)

    ML = int(W * 0.04)
    f_head = f("bahnschrift.ttf", int(H * 0.068))
    f_item = f("segoeui.ttf", max(14, int(H * 0.03)))

    before, after = extract_before_after(post.get("post", ""))
    if not before:
        before = ["Walk-in chaos", "No reminders sent", "Paper files lost", "Manual billing"]
    if not after:
        after  = ["Online booking 24/7", "Auto-reminders sent", "Digital records", "Instant billing"]

    bhh = wh(draw, "Ag", f_head)[1]
    draw.text((ML, int(H * 0.07)), "BEFORE", font=f_head, fill=(220, 80, 70))
    draw.rectangle([ML, int(H * 0.07) + bhh + 4, ML + 60, int(H * 0.07) + bhh + 7], fill=(220, 80, 70))

    cy = int(H * 0.07) + bhh + 22
    item_lh = wh(draw, "Ag", f_item)[1]
    for item in before:
        max_w = SPLIT - ML - 16
        while wh(draw, item, f_item)[0] > max_w and len(item) > 10:
            item = item[:-4] + "..."
        draw.text((ML, cy), "X  " + item, font=f_item, fill=(255, 160, 155))
        cy += item_lh + int(H * 0.025)

    ax = SPLIT + int(W * 0.04)
    afh = wh(draw, "Ag", f_head)[1]
    draw.text((ax, int(H * 0.07)), "AFTER", font=f_head, fill=(70, 200, 190))
    draw.rectangle([ax, int(H * 0.07) + afh + 4, ax + 60, int(H * 0.07) + afh + 7], fill=(70, 200, 190))

    cy2 = int(H * 0.07) + afh + 22
    for item in after:
        max_w = W - ax - 16
        while wh(draw, item, f_item)[0] > max_w and len(item) > 10:
            item = item[:-4] + "..."
        draw.text((ax, cy2), "V  " + item, font=f_item, fill=(155, 240, 230))
        cy2 += item_lh + int(H * 0.025)

    title = clean(post.get("hook", "") or "No System vs Clinic Management System")
    f_t = f("georgiab.ttf", max(14, int(H * 0.03)))
    tw, _ = wh(draw, title[:80], f_t)
    draw.text(((W - min(tw, W - 40)) // 2, H - 44), title[:80], font=f_t, fill=(200, 195, 185))
    draw.text((W - 160, H - 20), "ClinicSmart SL", font=f("segoeui.ttf", 14), fill=(100, 130, 128))
    return img

# ── Template: QUOTE ───────────────────────────────────────────────────────────

def extract_quote(post_text: str) -> str:
    m = re.search(r'[\u201c\u2018"](.*?)[\u201d\u2019"]', post_text, re.S)
    if m:
        return m.group(1).strip()
    lines = [l.strip() for l in post_text.split("\n") if len(l.strip()) > 20]
    return lines[0][:160] if lines else "Better systems. Better care."

def tpl_quote(post: dict, W: int, H: int) -> Image.Image:
    acc  = pillar_accent(post.get("pillar", "Social Proof"))
    img  = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)

    for y in range(0, H, 32):
        for x in range(0, W, 32):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(14, 36, 34))

    f_big_q = f("georgiab.ttf", int(H * 0.45))
    qw, qh  = wh(draw, "\u201c", f_big_q)
    draw.text((-qw // 3, -qh // 3), "\u201c", font=f_big_q, fill=(22, 60, 56))

    draw.rectangle([0, 0, W, 6], fill=acc)

    ML    = int(W * 0.08)
    max_w = W - 2 * ML
    quote = clean(extract_quote(post.get("post", "")))

    fnt_q = f("georgiab.ttf", 30)
    for sz in range(68, 20, -2):
        fnt_q = f("georgiab.ttf", sz)
        wrapped = wrap_px(draw, quote, fnt_q, max_w)
        lh = wh(draw, "Ag", fnt_q)[1]
        if lh * len(wrapped) + 8 * (len(wrapped) - 1) <= H * 0.5 and len(wrapped) <= 5:
            break

    lh      = wh(draw, "Ag", fnt_q)[1]
    total_h = lh * len(wrapped) + 8 * (len(wrapped) - 1)
    cy      = (H - total_h) // 2 - int(H * 0.06)

    for line in wrapped:
        lw, _ = wh(draw, line, fnt_q)
        draw.text(((W - lw) // 2, cy), line, font=fnt_q, fill=CREAM)
        cy += lh + 8

    f_attr = f("segoeui.ttf", max(15, int(H * 0.03)))
    attr   = "— Clinic owner, Sri Lanka"
    aw, _  = wh(draw, attr, f_attr)
    draw.text(((W - aw) // 2, cy + 28), attr, font=f_attr, fill=(120, 160, 155))

    draw.rectangle([0, H - 6, W, H], fill=acc)
    draw.text((W - 170, H - 30), "ClinicSmart SL", font=f("segoeui.ttf", 14), fill=(80, 120, 116))
    return img

# ── Template: STATS ───────────────────────────────────────────────────────────

def extract_stat(post_text: str, hook: str = "") -> str:
    combined = hook + " " + post_text
    patterns = [
        r"(\d[\d,]*\s*(?:minutes?|mins?|hours?|%|clinics?|patients?))",
        r"(Rs\.\s*[\d,]+)",
        r"(\d+\s*(?:out of|of)\s*\d+)",
        r"(\d+%)",
    ]
    for pat in patterns:
        m = re.search(pat, combined, re.I)
        if m:
            return m.group(1).strip()
    return "47 min"

def tpl_stats(post: dict, W: int, H: int) -> Image.Image:
    acc  = pillar_accent(post.get("pillar", "Educational"))
    img  = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    SPLIT = int(W * 0.52)
    draw.rectangle([SPLIT, 0, W, H], fill=DARK)

    ML = int(W * 0.046)
    dot_texture(draw, ML, 0, SPLIT - 20, H)
    accent_bar_left(draw, H, acc)

    stat = clean(extract_stat(post.get("post", ""), post.get("hook", ""))).upper()

    fnt_s = f("bahnschrift.ttf", 40)
    for sz in range(180, 40, -4):
        fnt_s = f("bahnschrift.ttf", sz)
        sw, sh = wh(draw, stat, fnt_s)
        if sw <= SPLIT - ML - 24 and sh <= H * 0.42:
            break

    sw, sh = wh(draw, stat, fnt_s)
    draw.text((ML, int(H * 0.15)), stat, font=fnt_s, fill=acc)

    hook = clean(post.get("hook", "") or post.get("post", "").split("\n")[0])
    hook = re.sub(r"^[•\-\u2013\u2014*]+\s*", "", hook)

    f_ctx   = f("georgiab.ttf", max(18, int(H * 0.038)))
    ctx_lns = wrap_px(draw, hook, f_ctx, SPLIT - ML - 24)[:3]

    cy = int(H * 0.15) + sh + 18
    draw.rectangle([ML, cy, ML + 56, cy + 3], fill=acc)
    cy += 18

    for line in ctx_lns:
        draw.text((ML, cy), line, font=f_ctx, fill=INK)
        cy += wh(draw, "Ag", f_ctx)[1] + 6

    tag = (post.get("hashtags") or ["#SriLankaHealthcare"])[0]
    hashtag_stamp(draw, H, clean(tag), ML)

    pillar_name = post.get("pillar", "Educational").upper()
    f_pl = f("segoeuib.ttf", max(13, int(H * 0.022)))
    plw, plh = wh(draw, pillar_name, f_pl)
    px = SPLIT + (W - SPLIT - plw) // 2
    py = int(H * 0.12)
    draw.rounded_rectangle([px - 8, py - 4, px + plw + 8, py + plh + 4], radius=4, fill=acc)
    draw.text((px, py), pillar_name, font=f_pl, fill=WHITE)

    body      = clean(post.get("post", ""))
    sentences = [s.strip() for s in re.split(r"[.!?]", body) if len(s.strip()) > 30]
    takeaway  = sentences[-1][:120] if sentences else "Digital clinics outperform paper-based ones."

    f_take = f("segoeui.ttf", max(14, int(H * 0.028)))
    rx, ry = SPLIT + int(W * 0.03), int(H * 0.35)
    rw     = W - rx - int(W * 0.03)
    for line in wrap_px(draw, takeaway, f_take, rw)[:5]:
        draw.text((rx, ry), line, font=f_take, fill=(180, 200, 198))
        ry += wh(draw, "Ag", f_take)[1] + 6

    brand_stamp(draw, W, H)
    divider_line(draw, SPLIT, H)
    return img

# ── Template: LIST ────────────────────────────────────────────────────────────

def extract_list_items(post_text: str) -> list:
    items = []
    for line in post_text.split("\n"):
        ls = clean(line).strip()
        m  = re.match(r"^[\d]+[.)]\s*(.+)", ls)
        if m:
            items.append(m.group(1).strip())
            continue
        m = re.match(r"^[\u2192\u2022\-\u2013]+\s*(.+)", ls)
        if m:
            items.append(m.group(1).strip())
    return items[:5]

def tpl_list(post: dict, W: int, H: int) -> Image.Image:
    acc  = pillar_accent(post.get("pillar", "Educational"))
    img  = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)

    for y in range(0, H, 30):
        for x in range(0, W, 30):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(12, 32, 30))

    accent_bar_left(draw, H, acc)

    ML  = int(W * 0.055)
    TOP = int(H * 0.08)

    hook = clean(post.get("hook", "") or post.get("post", "").split("\n")[0])
    hook = re.sub(r"^[•\-\u2013\u2014*]+\s*", "", hook)

    f_head    = f("bahnschrift.ttf", max(22, int(H * 0.055)))
    MAX_HEAD_W = W - ML - int(W * 0.04)
    head_lines = wrap_px(draw, hook, f_head, MAX_HEAD_W)[:2]
    lh_head    = wh(draw, "Ag", f_head)[1]

    cy = TOP
    for line in head_lines:
        draw.text((ML, cy), line, font=f_head, fill=WHITE)
        cy += lh_head + 4
    draw.rectangle([ML, cy + 8, ML + 72, cy + 11], fill=acc)
    cy += 30

    items = extract_list_items(post.get("post", ""))
    if not items:
        items = ["Digital appointment booking", "Automated reminders",
                 "Searchable patient records", "Live billing system",
                 "Real-time data dashboard"]

    f_num  = f("bahnschrift.ttf", max(20, int(H * 0.05)))
    f_item = f("segoeui.ttf",     max(14, int(H * 0.03)))
    num_w  = wh(draw, "5", f_num)[0] + 12
    ITEM_H = max(52, int(H * 0.115))
    GAP    = int(H * 0.016)
    item_x = ML + num_w + 18

    available_h   = H - cy - 60
    total_items_h = len(items) * ITEM_H + (len(items) - 1) * GAP
    if total_items_h > available_h:
        scale  = available_h / total_items_h
        ITEM_H = max(40, int(ITEM_H * scale))
        GAP    = int(GAP * scale)

    for i, item in enumerate(items):
        ty0      = cy + i * (ITEM_H + GAP)
        ty1      = ty0 + ITEM_H
        tile_acc = OPT_ACC[i % len(OPT_ACC)]
        tbg      = tuple(min(255, v + 20) for v in DARK)
        draw.rounded_rectangle([ML, ty0, W - int(W * 0.04), ty1], radius=6, fill=tbg)
        draw.rounded_rectangle([ML, ty0, ML + 4, ty1], radius=2, fill=tile_acc)
        num_str  = str(i + 1)
        nw, nh   = wh(draw, num_str, f_num)
        draw.text((ML + (num_w - nw) // 2, ty0 + (ITEM_H - nh) // 2),
                  num_str, font=f_num, fill=tile_acc)
        max_iw = W - item_x - int(W * 0.06)
        while wh(draw, item, f_item)[0] > max_iw and len(item) > 8:
            item = item[:-4] + "..."
        _, ih = wh(draw, item, f_item)
        draw.text((item_x, ty0 + (ITEM_H - ih) // 2), item, font=f_item, fill=WHITE)

    tag = (post.get("hashtags") or ["#SriLankaHealthcare"])[0]
    hashtag_stamp(draw, H, clean(tag), ML)
    draw.text((W - 170, H - 34), "ClinicSmart SL", font=f("segoeui.ttf", 15), fill=(75, 100, 97))
    return img

# ── Template: HOLIDAY ─────────────────────────────────────────────────────────

def tpl_holiday(post: dict, W: int, H: int) -> Image.Image:
    acc  = pillar_accent(post.get("pillar", "Engagement"))
    img  = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)

    CX, CY = W // 2, H // 2
    for r in range(max(W, H), 0, -60):
        alpha = max(10, 30 - r // 30)
        col   = tuple(min(255, v + alpha) for v in DARK)
        draw.ellipse([CX - r, CY - r, CX + r, CY + r], outline=col, width=1)
    for r in range(200, 0, -20):
        factor   = (200 - r) / 200
        warm_col = (int(DARK[0] + factor * 40), int(DARK[1] + factor * 28), int(DARK[2] + factor * 12))
        draw.ellipse([CX - r, CY - r, CX + r, CY + r], fill=warm_col)

    draw.rectangle([0, 0, W, 8], fill=acc)
    draw.rectangle([0, H - 8, W, H], fill=acc)

    post_text  = clean(post.get("post", ""))
    lines_raw  = post_text.split("\n")

    greeting = ""
    for line in lines_raw:
        lc = line.strip()
        if any(k in lc.lower() for k in
               ["happy", "wish", "joyful", "blessed", "new year", "avurudu",
                "easter", "good friday", "peace", "wishing"]):
            greeting = clean(lc)[:100]
            break
    if not greeting:
        date_str = post.get("date", "")
        greeting = date_str.split("  ")[1] if "  " in date_str else "A Special Day"

    MAX_W = int(W * 0.78)
    fnt_g = f("georgiab.ttf", 30)
    for sz in range(72, 20, -2):
        fnt_g   = f("georgiab.ttf", sz)
        wrapped = wrap_px(draw, greeting, fnt_g, MAX_W)
        lh      = wh(draw, "Ag", fnt_g)[1]
        if lh * len(wrapped) + 8 * (len(wrapped) - 1) <= H * 0.35:
            break

    lh      = wh(draw, "Ag", fnt_g)[1]
    total_h = lh * len(wrapped) + 8 * (len(wrapped) - 1)
    cy      = CY - total_h // 2 - int(H * 0.08)

    for line in wrapped:
        lw, _ = wh(draw, line, fnt_g)
        draw.text(((W - lw) // 2, cy), line, font=fnt_g, fill=CREAM)
        cy += lh + 8

    draw.rectangle([(W - 80) // 2, cy + 12, (W + 80) // 2, cy + 15], fill=acc)

    f_sub  = f("segoeui.ttf", max(15, int(H * 0.028)))
    cy    += 30
    sub_lines = [l.strip() for l in lines_raw
                 if l.strip() and l.strip() != greeting and len(l.strip()) > 8][:3]
    for sub in sub_lines:
        sc  = clean(sub)
        sw, _ = wh(draw, sc, f_sub)
        draw.text(((W - min(sw, W - 60)) // 2, cy), sc, font=f_sub, fill=(170, 200, 195))
        cy += wh(draw, "Ag", f_sub)[1] + 6

    brand_stamp(draw, W, H, clr=(100, 150, 148))
    return img

# ── Template: TIP ─────────────────────────────────────────────────────────────

def tpl_tip(post: dict, W: int, H: int) -> Image.Image:
    acc  = pillar_accent(post.get("pillar", "Educational"))
    img  = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    for y in range(0, H, 36):
        draw.rectangle([0, y, W, y + 1], fill=(235, 232, 224))

    accent_bar_left(draw, H, acc)

    ML  = int(W * 0.06)
    TOP = int(H * 0.09)

    f_badge   = f("segoeuib.ttf", max(13, int(H * 0.026)))
    badge_txt = "CLINIC TIP"
    bw, bh    = wh(draw, badge_txt, f_badge)
    bp        = int(H * 0.014)
    draw.rounded_rectangle([ML, TOP, ML + bw + bp * 2, TOP + bh + bp * 2], radius=4, fill=acc)
    draw.text((ML + bp, TOP + bp), badge_txt, font=f_badge, fill=WHITE)

    cy = TOP + bh + bp * 2 + int(H * 0.04)

    body  = clean(post.get("post", ""))
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    if lines and any(k in lines[0].lower() for k in ("tip", "did you know", "clinic tip")):
        lines = lines[1:]

    tip_text = " ".join(lines[:2])[:200] if len(lines) >= 2 else (lines[0] if lines else "Better systems. Less stress.")
    MAX_TXT_W = W - ML - int(W * 0.06)

    fnt_tip = f("bahnschrift.ttf", 30)
    for sz in range(56, 18, -2):
        fnt_tip = f("bahnschrift.ttf", sz)
        wrapped = wrap_px(draw, tip_text, fnt_tip, MAX_TXT_W)
        lh      = wh(draw, "Ag", fnt_tip)[1]
        if lh * len(wrapped) + 6 * (len(wrapped) - 1) <= H * 0.42:
            break

    lh_tip = wh(draw, "Ag", fnt_tip)[1]
    for line in wrapped:
        clr = acc if line == wrapped[-1] else INK
        draw.text((ML, cy), line, font=fnt_tip, fill=clr)
        cy += lh_tip + 6

    draw.rectangle([ML, cy + 12, ML + 64, cy + 15], fill=acc)
    cy += 28

    action_lines = [l.strip() for l in body.split("\n") if l.strip()]
    action = clean(action_lines[-1])[:100] if action_lines else "Comment DEMO below."
    f_act  = f("segoeui.ttf", max(15, int(H * 0.03)))
    for line in wrap_px(draw, action, f_act, MAX_TXT_W):
        draw.text((ML, cy), line, font=f_act, fill=DIM)
        cy += wh(draw, "Ag", f_act)[1] + 4

    tag = (post.get("hashtags") or ["#SriLankaHealthcare"])[0]
    hashtag_stamp(draw, H, clean(tag), ML)
    brand_stamp(draw, W, H)
    return img

# ── Template: DEBATE ──────────────────────────────────────────────────────────

def tpl_debate(post: dict, W: int, H: int) -> Image.Image:
    RED  = (180, 40, 32)
    img  = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)

    for x in range(-H, W + H, 40):
        draw.line([(x, 0), (x + H, H)], fill=(18, 42, 40), width=2)

    draw.rectangle([0, 0, W, int(H * 0.12)], fill=RED)
    f_badge = f("segoeuib.ttf", max(14, int(H * 0.036)))
    badge   = "HOT TAKE"
    bw, bh  = wh(draw, badge, f_badge)
    draw.text(((W - bw) // 2, (int(H * 0.12) - bh) // 2), badge, font=f_badge, fill=WHITE)

    body = clean(post.get("post", ""))
    hot  = ""
    for line in body.split("\n"):
        lc = line.strip()
        if ":" in lc and len(lc) > 20:
            hot = lc.split(":", 1)[-1].strip()
            if hot:
                break
    if not hot:
        hot = clean(post.get("hook", "") or body.split("\n")[0])
    hot = hot[:160]

    ML    = int(W * 0.06)
    MAX_W = W - 2 * ML
    fnt_h = f("bahnschrift.ttf", 40)
    for sz in range(72, 22, -2):
        fnt_h   = f("bahnschrift.ttf", sz)
        wrapped = wrap_px(draw, hot, fnt_h, MAX_W)
        lh      = wh(draw, "Ag", fnt_h)[1]
        if lh * len(wrapped) + 8 * (len(wrapped) - 1) <= H * 0.42:
            break

    lh      = wh(draw, "Ag", fnt_h)[1]
    total_h = lh * len(wrapped) + 8 * (len(wrapped) - 1)
    cy      = int(H * 0.16) + int((H * 0.55 - total_h) // 2)

    for i, line in enumerate(wrapped):
        clr = WHITE if i < len(wrapped) - 1 else (255, 180, 50)
        lw, _ = wh(draw, line, fnt_h)
        draw.text(((W - lw) // 2, cy), line, font=fnt_h, fill=clr)
        cy += lh + 8

    f_sub  = f("segoeui.ttf", max(16, int(H * 0.032)))
    prompt = "Agree or Disagree? Comment below."
    pw, _  = wh(draw, prompt, f_sub)
    draw.text(((W - pw) // 2, H - int(H * 0.14)), prompt, font=f_sub, fill=(160, 190, 185))

    draw.rectangle([0, H - int(H * 0.07), W, H], fill=RED)
    tag = (post.get("hashtags") or ["#SriLankaHealthcare"])[0]
    tc  = clean(tag)
    tw, _ = wh(draw, tc, f("segoeuib.ttf", 16))
    draw.text(((W - tw) // 2, H - int(H * 0.07) + int(H * 0.022)),
              tc, font=f("segoeuib.ttf", 16), fill=WHITE)
    draw.text((W - 170, H - 20), "ClinicSmart SL", font=f("segoeui.ttf", 14), fill=(180, 180, 180))
    return img

# ── Template: BEHIND THE SCENES ───────────────────────────────────────────────

def tpl_bts(post: dict, W: int, H: int) -> Image.Image:
    acc  = pillar_accent(post.get("pillar", "Behind the Scenes"))
    img  = Image.new("RGB", (W, H), (10, 35, 25))
    draw = ImageDraw.Draw(img)

    for y in range(0, H, 22):
        for x in range(0, W, 22):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(14, 42, 32))

    accent_bar_left(draw, H, acc)

    ML  = int(W * 0.055)
    TOP = int(H * 0.08)

    f_badge = f("segoeuib.ttf", max(12, int(H * 0.022)))
    bh      = wh(draw, "Ag", f_badge)[1]
    draw.rounded_rectangle([ML, TOP, ML + 220, TOP + bh + 12], radius=4, fill=acc)
    draw.text((ML + 10, TOP + 6), "BEHIND THE SCENES", font=f_badge, fill=WHITE)

    cy = TOP + bh + 28

    body  = clean(post.get("post", ""))
    lines = [l.strip() for l in body.split("\n") if l.strip()]

    headline  = lines[0][:120] if lines else "A day in the life of a Sri Lankan clinic."
    MAX_TXT_W = W - ML - int(W * 0.06)

    fnt_h = f("bahnschrift.ttf", 30)
    for sz in range(60, 18, -2):
        fnt_h   = f("bahnschrift.ttf", sz)
        wrapped = wrap_px(draw, headline, fnt_h, MAX_TXT_W)
        lh      = wh(draw, "Ag", fnt_h)[1]
        if lh * len(wrapped) + 6 * (len(wrapped) - 1) <= H * 0.35:
            break

    lh_h = wh(draw, "Ag", fnt_h)[1]
    for line in wrapped:
        draw.text((ML, cy), line, font=fnt_h, fill=CREAM)
        cy += lh_h + 6

    draw.rectangle([ML, cy + 12, ML + 64, cy + 15], fill=acc)
    cy += 28

    snippet = " ".join(lines[1:4])[:200]
    if snippet:
        f_snip = f("segoeui.ttf", max(15, int(H * 0.028)))
        for line in wrap_px(draw, snippet, f_snip, MAX_TXT_W)[:4]:
            draw.text((ML, cy), line, font=f_snip, fill=(160, 200, 185))
            cy += wh(draw, "Ag", f_snip)[1] + 5

    tag = (post.get("hashtags") or ["#SriLankaHealthcare"])[0]
    hashtag_stamp(draw, H, clean(tag), ML)
    brand_stamp(draw, W, H, clr=(80, 140, 110))
    return img

# ── Template: CAROUSEL ────────────────────────────────────────────────────────

def tpl_carousel(post: dict, W: int, H: int) -> Image.Image:
    acc     = pillar_accent(post.get("pillar", "Educational"))
    is_reel = "reel" in post.get("type", "").lower()
    img     = Image.new("RGB", (W, H), DARK)
    draw    = ImageDraw.Draw(img)

    for y in range(0, H, 26):
        for x in range(0, W, 26):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(14, 34, 32))

    accent_bar_left(draw, H, acc)
    draw.rectangle([0, H - 6, W, H], fill=acc)

    ML  = int(W * 0.06)
    TOP = int(H * 0.1)

    badge    = "REEL COVER" if is_reel else "SWIPE"
    f_badge  = f("segoeuib.ttf", max(12, int(H * 0.026)))
    bw, bh   = wh(draw, badge, f_badge)
    draw.rounded_rectangle([ML, TOP, ML + bw + 18, TOP + bh + 10], radius=4, fill=acc)
    draw.text((ML + 9, TOP + 5), badge, font=f_badge, fill=WHITE)

    cy = TOP + bh + 26

    slides = post.get("slides", [])
    hook   = clean(slides[0] if slides else post.get("post", "").split("\n")[0])
    hook   = re.sub(r"^[•\-\u2013\u2014*]+\s*", "", hook)[:180]

    MAX_TXT_W = W - ML - int(W * 0.06)
    fnt_h = f("bahnschrift.ttf", 30)
    for sz in range(84, 20, -2):
        fnt_h   = f("bahnschrift.ttf", sz)
        wrapped = wrap_px(draw, hook, fnt_h, MAX_TXT_W)
        lh      = wh(draw, "Ag", fnt_h)[1]
        if lh * len(wrapped) + 6 * (len(wrapped) - 1) <= H * 0.48:
            break

    lh = wh(draw, "Ag", fnt_h)[1]
    for i, line in enumerate(wrapped):
        clr = acc if i == len(wrapped) - 1 else CREAM
        draw.text((ML, cy), line, font=fnt_h, fill=clr)
        cy += lh + 6

    draw.rectangle([ML, cy + 12, ML + 64, cy + 15], fill=acc)
    cy += 28

    if slides and not is_reel:
        f_cnt = f("segoeuib.ttf", max(13, int(H * 0.024)))
        draw.text((ML, cy), f"{len(slides)} SLIDES INSIDE", font=f_cnt, fill=(150, 190, 185))

    tag = (post.get("hashtags") or ["#SriLankaHealthcare"])[0]
    hashtag_stamp(draw, H, clean(tag), ML)
    brand_stamp(draw, W, H)

    f_arrow = f("segoeuib.ttf", max(20, int(H * 0.042)))
    arrow   = "SWIPE ->" if not is_reel else "WATCH >"
    aw, ah  = wh(draw, arrow, f_arrow)
    draw.text((W - aw - ML, H - ah - int(H * 0.07)), arrow, font=f_arrow, fill=acc)
    return img

# ── Dispatcher ────────────────────────────────────────────────────────────────

TEMPLATE_FN = {
    "POLL":         tpl_poll,
    "HOOK":         tpl_hook,
    "BEFORE_AFTER": tpl_before_after,
    "QUOTE":        tpl_quote,
    "STATS":        tpl_stats,
    "LIST":         tpl_list,
    "HOLIDAY":      tpl_holiday,
    "TIP":          tpl_tip,
    "DEBATE":       tpl_debate,
    "BTS":          tpl_bts,
    "CAROUSEL":     tpl_carousel,
}

# ── Main ──────────────────────────────────────────────────────────────────────

def generate_all():
    with open("posts.json", encoding="utf-8") as fh:
        posts = json.load(fh)

    total   = len(posts)
    success = 0
    errors  = []
    print(f"\nGenerating {total} post images...\n")

    for i, post in enumerate(posts, 1):
        platform = post.get("platform", "LinkedIn").lower().replace(" ", "")
        day      = post.get("day", 0)
        ptype    = post.get("type", "").lower().replace(" ", "_")[:28]
        tpl_name = detect_template(post)
        tpl_fn   = TEMPLATE_FN[tpl_name]

        safe_type = re.sub(r"[^a-z0-9_]", "_", ptype)
        filename  = f"day{day:02d}_{safe_type}_{tpl_name.lower()}.png"
        out_path  = Path(f"output/{platform}") / filename

        try:
            W, H = SIZES.get(platform, SIZES["linkedin"])
            img  = tpl_fn(post, W, H)
            img.save(str(out_path), "PNG")
            success += 1
            print(f"  [{i:02d}/{total}] {platform:10s}  Day {day:02d}  {tpl_name:12s}  {filename}")
        except Exception as e:
            err = f"  [ERR] Day {day} {platform} {tpl_name}: {e}"
            errors.append(err)
            print(err)

    print(f"\nDone: {success}/{total} images saved.")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(e)
    print("\nOutput: output/linkedin/  output/facebook/  output/instagram/")

if __name__ == "__main__":
    generate_all()
