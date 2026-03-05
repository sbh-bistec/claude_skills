"""
generate_posts.py
-----------------
Reads posts.json and generates high-quality branded PNG images
using the canvas-design skill fonts (Clinical Clarity design system).

Usage:
    python generate_posts.py

Output:
    output/linkedin/day01_linkedin.png
    output/facebook/day01_facebook.png
    output/instagram/day01_instagram.png
    ...

Requirements:
    pip install pillow
"""

import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# ── Font directory (canvas-design skill) ──────────────────────────────────────

FONTS_DIR = Path(__file__).parent / ".claude" / "skills" / "canvas-design" / "canvas-fonts"


# ── Platform config ────────────────────────────────────────────────────────────

PLATFORMS = {
    "LinkedIn":  {"size": (1200, 627),  "slug": "linkedin"},
    "Facebook":  {"size": (1200, 630),  "slug": "facebook"},
    "Instagram": {"size": (1080, 1080), "slug": "instagram"},
}


# ── Brand colours per content pillar ──────────────────────────────────────────

PILLARS = {
    "Educational":    {"bg": "#EDF6F5", "accent": "#0D7377", "dark": "#083D40", "tag": "EDUCATIONAL"},
    "Before & After": {"bg": "#EEEEF8", "accent": "#3B4EC8", "dark": "#1A2080", "tag": "BEFORE & AFTER"},
    "Social Proof":   {"bg": "#F2EEFA", "accent": "#6D3FC0", "dark": "#3A1880", "tag": "SOCIAL PROOF"},
    "Engagement":     {"bg": "#FEF8EC", "accent": "#C07A0A", "dark": "#7A4800", "tag": "ENGAGEMENT"},
    "Promotional":    {"bg": "#FAEEED", "accent": "#B83025", "dark": "#6E1310", "tag": "PROMOTIONAL"},
    "General":        {"bg": "#F4F4F0", "accent": "#3A4150", "dark": "#1A1E28", "tag": "POST"},
}

BRAND_NAME = "ClinicSmart SL"


# ── Colour helpers ─────────────────────────────────────────────────────────────

def hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def blend(base: tuple, overlay: tuple, alpha: float) -> tuple:
    return tuple(int(b * (1 - alpha) + o * alpha) for b, o in zip(base, overlay))


# ── Font loader ────────────────────────────────────────────────────────────────

_cache: dict = {}


def get_font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    key = (filename, size)
    if key not in _cache:
        path = FONTS_DIR / filename
        try:
            _cache[key] = ImageFont.truetype(str(path), size)
        except (IOError, OSError):
            _cache[key] = ImageFont.load_default()
    return _cache[key]


# Semantic helpers
def font_hook(sz):    return get_font("Gloock-Regular.ttf",            sz)  # serif headlines
def font_body(sz):    return get_font("InstrumentSans-Regular.ttf",    sz)  # body copy
def font_bold(sz):    return get_font("InstrumentSans-Bold.ttf",       sz)  # bold labels
def font_label(sz):   return get_font("BricolageGrotesque-Bold.ttf",   sz)  # badges / tags
def font_display(sz): return get_font("WorkSans-Bold.ttf",             sz)  # giant day number
def font_mono(sz):    return get_font("DMMono-Regular.ttf",            sz)  # time / metadata


# ── Text sanitiser ────────────────────────────────────────────────────────────

import re

def clean(text: str) -> str:
    """Strip emoji and non-latin characters the canvas fonts can't render."""
    # Remove emoji (Unicode ranges for emoji/pictographs)
    emoji_re = re.compile(
        "["
        "\U0001F300-\U0001F9FF"   # misc symbols & pictographs
        "\U00002702-\U000027B0"   # dingbats
        "\U000024C2-\U0001F251"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002500-\U00002BEF"   # box-drawing, arrows, etc.
        "\u200d"                   # zero-width joiner
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_re.sub("", text)
    # Strip non-printable chars but preserve newlines
    text = "".join(c for c in text if c.isprintable() or c == "\n")
    return text.strip()


# ── Text measurement ───────────────────────────────────────────────────────────

def measure(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple:
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1]


def wrap_px(draw: ImageDraw.ImageDraw, text: str, fnt, max_px: int) -> list:
    """Word-wrap text to fit within max_px pixels (pixel-accurate)."""
    words  = text.split()
    lines  = []
    line   = []
    for word in words:
        test = " ".join(line + [word])
        w, _ = measure(draw, test, fnt)
        if w > max_px and line:
            lines.append(" ".join(line))
            line = [word]
        else:
            line.append(word)
    if line:
        lines.append(" ".join(line))
    return lines or [""]


def wrap_paragraphs(draw, text: str, fnt, max_px: int) -> list:
    """Wrap each paragraph separately, preserving blank-line breaks."""
    result = []
    for para in text.split("\n"):
        para = para.strip()
        if para:
            result.extend(wrap_px(draw, para, fnt, max_px))
        else:
            if result and result[-1] != "":
                result.append("")
    return result


# ── Draw helpers ───────────────────────────────────────────────────────────────

def rrect(draw, x0, y0, x1, y1, r, fill):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill)


def centered_text(draw, cx, y, text, fnt, fill):
    w, _ = measure(draw, text, fnt)
    draw.text((cx - w // 2, y), text, font=fnt, fill=fill)


# ── LinkedIn / Facebook (horizontal) ──────────────────────────────────────────

def build_horizontal(post: dict, W: int, H: int) -> Image.Image:
    p      = PILLARS.get(post.get("pillar", "General"), PILLARS["General"])
    bg     = hex_rgb(p["bg"])
    accent = hex_rgb(p["accent"])
    dark   = hex_rgb(p["dark"])
    white  = (255, 255, 255)
    ink    = (18, 20, 28)

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # ── Right dark panel ──────────────────────────────────────────────────────
    RBAR = int(W * 0.30)
    rx   = W - RBAR
    draw.rectangle([rx, 0, W, H], fill=dark)

    # Ghost day number — enormous, barely visible
    day_str = f"{post['day']:02d}"
    day_fnt = font_display(int(H * 1.5))
    dw, dh  = measure(draw, day_str, day_fnt)
    ghost   = blend(dark, white, 0.07)
    draw.text((rx + (RBAR - dw) // 2, (H - dh) // 2 - int(H * 0.06)),
              day_str, font=day_fnt, fill=ghost)

    # Pillar tag badge (centred in right panel)
    tag_fnt = font_label(int(H * 0.030))
    tag     = p["tag"]
    tw, th  = measure(draw, tag, tag_fnt)
    tx      = rx + (RBAR - tw) // 2
    ty      = int(H * 0.12)
    rrect(draw, tx - 16, ty - 8, tx + tw + 16, ty + th + 8, 4, accent)
    draw.text((tx, ty), tag, font=tag_fnt, fill=white)

    # Date below badge
    date_str = post.get("date", "")
    date_fnt = font_body(int(H * 0.022))
    daw, _   = measure(draw, date_str, date_fnt)
    centered_text(draw, rx + RBAR // 2, ty + th + 22,
                  date_str, date_fnt, blend(dark, white, 0.45))

    # Platform name near bottom
    plat_fnt = font_label(int(H * 0.026))
    plat_str = post["platform"].upper()
    centered_text(draw, rx + RBAR // 2, H - int(H * 0.15),
                  plat_str, plat_fnt, blend(dark, white, 0.30))

    # Brand name at bottom
    brand_fnt = font_body(int(H * 0.020))
    centered_text(draw, rx + RBAR // 2, H - int(H * 0.08),
                  BRAND_NAME, brand_fnt, blend(dark, white, 0.45))

    # Thin accent rule at bottom of right panel
    draw.rectangle([rx, H - 5, W, H], fill=accent)

    # ── Left content area ─────────────────────────────────────────────────────
    ML     = int(W * 0.055)          # left margin
    MR     = rx - int(W * 0.04)      # right boundary of content area
    CW     = MR - ML                 # usable width

    # 5-px left accent strip
    draw.rectangle([0, 0, 5, H], fill=accent)

    cursor = int(H * 0.095)

    # Time stamp (monospace, accent colour)
    time_str = post.get("time", "")
    if time_str:
        t_fnt = font_mono(int(H * 0.021))
        draw.text((ML, cursor), f">  {time_str}", font=t_fnt, fill=accent)
        cursor += int(H * 0.058)

    # Hook  (Gloock serif — the centrepiece)
    hook = clean(post.get("hook") or "").strip()
    if hook:
        h_sz    = int(H * 0.056)
        h_fnt   = font_hook(h_sz)
        h_lines = wrap_px(draw, f'"{hook}"', h_fnt, CW)[:3]
        for line in h_lines:
            draw.text((ML, cursor), line, font=h_fnt, fill=ink)
            _, lh   = measure(draw, line or "A", h_fnt)
            cursor += lh + int(H * 0.010)
        cursor += int(H * 0.018)

        # Short accent rule below hook
        draw.rectangle([ML, cursor, ML + int(CW * 0.10), cursor + 3], fill=accent)
        cursor += int(H * 0.030)

    # Body text (Instrument Sans Regular)
    body = clean(post.get("post") or "").strip()
    if body:
        b_sz      = int(H * 0.029)
        b_fnt     = font_body(b_sz)
        b_lines   = wrap_paragraphs(draw, body, b_fnt, CW)
        _, line_h = measure(draw, "A", b_fnt)
        line_h   += int(H * 0.009)
        reserve   = int(H * 0.14)    # space for hashtag strip + margin

        for line in b_lines:
            if cursor + line_h > H - reserve:
                draw.text((ML, cursor), "…", font=b_fnt, fill=(160, 162, 170))
                break
            colour = (42, 48, 60) if not line else (70, 76, 90)
            draw.text((ML, cursor), line, font=b_fnt, fill=colour)
            cursor += line_h

    # Hashtag strip
    hashtags = post.get("hashtags", [])
    if hashtags:
        hash_fnt = font_label(int(H * 0.021))
        tags_str = "  ".join(hashtags[:5])
        hy       = H - int(H * 0.090)
        draw.text((ML, hy), tags_str, font=hash_fnt, fill=accent)

    # Thin accent rule at bottom of left panel
    draw.rectangle([6, H - 5, rx, H], fill=blend(bg, accent, 0.35))

    return img


# ── Instagram (square) ─────────────────────────────────────────────────────────

def build_instagram(post: dict, W: int, H: int) -> Image.Image:
    p      = PILLARS.get(post.get("pillar", "General"), PILLARS["General"])
    bg     = hex_rgb(p["bg"])
    accent = hex_rgb(p["accent"])
    dark   = hex_rgb(p["dark"])
    white  = (255, 255, 255)
    ink    = (18, 20, 28)

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    TOP_H = int(H * 0.42)

    # Dark top block
    draw.rectangle([0, 0, W, TOP_H], fill=dark)

    # Ghost day number in top block
    day_str = f"{post['day']:02d}"
    day_fnt = font_display(int(TOP_H * 1.8))
    dw, dh  = measure(draw, day_str, day_fnt)
    ghost   = blend(dark, white, 0.06)
    draw.text(((W - dw) // 2, (TOP_H - dh) // 2 - int(H * 0.02)),
              day_str, font=day_fnt, fill=ghost)

    # Pillar tag badge (centred, upper portion of top block)
    tag_fnt = font_label(int(H * 0.032))
    tag     = p["tag"]
    tw, th  = measure(draw, tag, tag_fnt)
    tx      = (W - tw) // 2
    ty      = int(TOP_H * 0.15)
    rrect(draw, tx - 20, ty - 10, tx + tw + 20, ty + th + 10, 6, accent)
    draw.text((tx, ty), tag, font=tag_fnt, fill=white)

    # Date below badge
    date_str = post.get("date", "")
    date_fnt = font_body(int(H * 0.026))
    centered_text(draw, W // 2, ty + th + 20,
                  date_str, date_fnt, blend(dark, white, 0.48))

    # Hook (large serif, centred, lower portion of top block)
    # Fallback: use first sentence of body text when there's no hook
    hook = clean(post.get("hook") or "").strip()
    if not hook:
        raw_body = clean(post.get("post") or "")
        first_sentence = re.split(r"(?<=[.!?])\s", raw_body, maxsplit=1)[0]
        hook = first_sentence[:120]   # cap length

    if hook:
        h_sz    = int(H * 0.048)
        h_fnt   = font_hook(h_sz)
        display = f'"{hook}"' if not hook.startswith('"') else hook
        h_lines = wrap_px(draw, display, h_fnt, int(W * 0.84))[:3]
        total_h = sum(measure(draw, l or "A", h_fnt)[1] + int(H * 0.010) for l in h_lines)
        hy      = TOP_H - total_h - int(H * 0.038)
        for line in h_lines:
            lw, lh = measure(draw, line or "A", h_fnt)
            draw.text(((W - lw) // 2, hy), line, font=h_fnt, fill=white)
            hy += lh + int(H * 0.010)

    # ── Bottom content block ───────────────────────────────────────────────────
    ML     = int(W * 0.07)
    CW     = W - ML * 2
    cursor = TOP_H + int(H * 0.042)

    # Centred accent divider
    div_w = int(CW * 0.10)
    draw.rectangle([(W - div_w) // 2, cursor,
                    (W + div_w) // 2, cursor + 3], fill=accent)
    cursor += int(H * 0.036)

    # Body excerpt
    body = clean(post.get("post") or "").strip()
    if body:
        b_sz      = int(H * 0.030)
        b_fnt     = font_body(b_sz)
        b_lines   = wrap_paragraphs(draw, body, b_fnt, CW)
        _, line_h = measure(draw, "A", b_fnt)
        line_h   += int(H * 0.009)
        reserve   = int(H * 0.15)

        for line in b_lines:
            if cursor + line_h > H - reserve:
                draw.text((ML, cursor), "…", font=b_fnt, fill=(160, 162, 170))
                break
            draw.text((ML, cursor), line, font=b_fnt, fill=(55, 60, 72))
            cursor += line_h

    # Hashtags (centred)
    hashtags = post.get("hashtags", [])
    if hashtags:
        hash_fnt = font_label(int(H * 0.023))
        tags_str = "  ".join(hashtags[:4])
        tw, _    = measure(draw, tags_str, hash_fnt)
        draw.text(((W - tw) // 2, H - int(H * 0.095)),
                  tags_str, font=hash_fnt, fill=accent)

    # Brand name (centred)
    brand_fnt = font_body(int(H * 0.022))
    bw, _     = measure(draw, BRAND_NAME, brand_fnt)
    draw.text(((W - bw) // 2, H - int(H * 0.042)),
              BRAND_NAME, font=brand_fnt, fill=(155, 158, 168))

    # Bottom accent strip
    draw.rectangle([0, H - 5, W, H], fill=accent)

    return img


# ── Dispatcher ─────────────────────────────────────────────────────────────────

def build_image(post: dict, platform: str) -> Image.Image:
    W, H = PLATFORMS[platform]["size"]
    if platform == "Instagram":
        return build_instagram(post, W, H)
    return build_horizontal(post, W, H)


# ── Batch generator ────────────────────────────────────────────────────────────

def generate_all(json_file: str = "posts.json") -> None:
    posts = json.loads(Path(json_file).read_text(encoding="utf-8"))

    for platform, cfg in PLATFORMS.items():
        Path(f"output/{cfg['slug']}").mkdir(parents=True, exist_ok=True)

    total  = 0
    errors = 0

    for post in posts:
        platform = post.get("platform", "")
        if platform not in PLATFORMS:
            continue

        slug = PLATFORMS[platform]["slug"]
        try:
            img      = build_image(post, platform)
            out_path = f"output/{slug}/day{post['day']:02d}_{slug}.png"
            img.save(out_path, "PNG")
            print(f"  [OK]  {out_path}")
            total += 1
        except Exception as e:
            print(f"  [ERR] Day {post['day']} {platform}: {e}")
            errors += 1

    print(f"\n{'-' * 48}")
    print(f"  Generated : {total} images")
    if errors:
        print(f"  Errors    : {errors}")
    print(f"  Location  : output/")
    print(f"{'-' * 48}")


if __name__ == "__main__":
    generate_all()
