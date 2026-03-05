
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Config ───────────────────────────────────────────────────────────────────

BASE_DIR = Path("c:/Users/ShaeelaHussain/Documents/sbh/claude_skill/t5/output")
DIRS = {
    "Facebook":  (1200, 630),
    "Instagram": (1080, 1080),
    "LinkedIn":  (1200, 627),
}

FONT_DIR = Path("C:/Windows/Fonts")

# ── Palette (Healthcare Theme from preview_day01.py) ─────────────────────────

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

# ── Helpers ──────────────────────────────────────────────────────────────────

def f(name: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FONT_DIR / name), size)
    except (IOError, OSError):
        # Fallback to standard fonts if specific ones are missing
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

def wh(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, fnt)
    return bb[2] - bb[0], bb[3] - bb[1]

def wrap_text(draw, text, font, max_width):
    lines = []
    words = text.split()
    if not words:
        return [""]
    
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + " " + word
        w, _ = wh(draw, test_line, font)
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

# ── Generator ────────────────────────────────────────────────────────────────

def generate_image(post: dict, platform: str):
    width, height = DIRS.get(platform, (1200, 630))
    img  = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(img)

    # Layout logic:
    if width == height:
        SPLIT = width // 2
    else:
        SPLIT = 540

    # ── Right dark panel ──────────────────────────────────────────────────────
    draw.rectangle([SPLIT, 0, width, height], fill=DARK)

    # Ghost Day Number
    day_str = f"{post['day']:02d}"
    f_ghost = f("bahnschrift.ttf", 310)
    gw, gh  = wh(draw, day_str, f_ghost)
    ghost_c = (12, 36, 33)
    
    # Center ghost in right panel
    right_center_x = SPLIT + (width - SPLIT) // 2
    draw.text((right_center_x - gw // 2, (height - gh) // 2 - 15),
              day_str, font=f_ghost, fill=ghost_c)

    # ── Right Panel Content ──────────────────────────────────────────────────
    # If Day 1, use the special Option Tiles (hardcoded for now as per preview_day01)
    # OR if the post text contains A) B) C) D) options, we could parse them.
    # For now, let's make a generic right panel for non-Day-1 posts.

    is_day_1 = post['day'] == 1 and "A)" in post.get('post', '')

    if is_day_1:
        # 4 stacked option tiles (Hardcoded for Day 1 style as requested)
        # Note: In a real dynamic system, we'd parse these options from the 'post' text.
        # But here we'll just use generic placeholders or the ones from the file if we can extract them.
        
        # Let's try to extract options from post text if available
        options = []
        lines = post.get('post', '').split('\n')
        for line in lines:
            if line.strip().startswith(('A)', 'B)', 'C)', 'D)')):
                parts = line.strip().split(')', 1)
                if len(parts) == 2:
                    options.append((parts[0].strip(), parts[1].strip().upper()))
        
        if not options:
             options = [
                ("A", "PATIENT APPOINTMENTS"),
                ("B", "BILLING & PAYMENTS"),
                ("C", "PATIENT RECORDS"),
                ("D", "STAFF COORDINATION"),
            ]

        TILE_W = 450
        # Adjust for Instagram square layout
        if width - SPLIT < 480: 
            TILE_W = width - SPLIT - 40
            
        TILE_H = 98
        TILE_G = 10
        tile_x = SPLIT + (width - SPLIT - TILE_W) // 2
        tiles_h = len(options) * TILE_H + (len(options)-1) * TILE_G
        tile_y  = (height - tiles_h) // 2

        f_letter = f("bahnschrift.ttf", 36)
        f_opt    = f("segoeuib.ttf",    19)

        for i, (letter, name) in enumerate(options[:4]): # Max 4
            acc  = OPT_ACC[i % len(OPT_ACC)]
            ty0  = tile_y + i * (TILE_H + TILE_G)
            ty1  = ty0 + TILE_H
            tbg  = tuple(min(255, v + 16) for v in DARK)

            draw.rounded_rectangle([tile_x, ty0, tile_x + TILE_W, ty1],
                                    radius=6, fill=tbg)
            draw.rounded_rectangle([tile_x, ty0, tile_x + 5, ty1],
                                    radius=3, fill=acc)
            
            BR = 20
            bx = tile_x + 40
            by = ty0 + TILE_H // 2
            draw.ellipse([bx - BR, by - BR, bx + BR, by + BR], fill=acc)
            lw, lh = wh(draw, letter, f_letter)
            draw.text((bx - lw // 2, by - lh // 2 - 1), letter, font=f_letter, fill=WHITE)
            
            nw, nh = wh(draw, name, f_opt)
            # Clip text if too long
            if nw > TILE_W - 100:
                name = name[:30] + "..."
                nw, nh = wh(draw, name, f_opt)
            draw.text((tile_x + 76, ty0 + (TILE_H - nh) // 2), name, font=f_opt, fill=WHITE)
            
            draw.rectangle([tile_x + TILE_W - 60, ty1 - 3,
                            tile_x + TILE_W - 4,  ty1 - 1], fill=acc)

    else:
        # Standard Right Panel for other days
        # Display Pillar, Date, Platform
        
        # Pillar Badge
        pillar = post.get('pillar', 'General').upper()
        f_pillar = f("segoeuib.ttf", 24)
        pw, ph = wh(draw, pillar, f_pillar)
        
        px = right_center_x
        py = height // 2 - 40
        
        # Accent color based on pillar hash or random from palette
        acc_idx = len(pillar) % len(OPT_ACC)
        acc = OPT_ACC[acc_idx]
        
        # Draw badge
        pad_x, pad_y = 30, 15
        draw.rounded_rectangle([px - pw//2 - pad_x, py - pad_y, px + pw//2 + pad_x, py + ph + pad_y],
                               radius=8, fill=acc)
        draw.text((px - pw//2, py), pillar, font=f_pillar, fill=WHITE)
        
        # Date
        date_str = post.get('date', '')
        f_date = f("georgia.ttf", 20)
        dw, dh = wh(draw, date_str, f_date)
        draw.text((px - dw//2, py + ph + 40), date_str, font=f_date, fill=DIM)
        
        # Platform
        f_plat = f("segoeui.ttf", 16)
        plat_str = platform.upper()
        plw, plh = wh(draw, plat_str, f_plat)
        draw.text((px - plw//2, height - 60), plat_str, font=f_plat, fill=(75, 100, 97))


    # Brand name bottom-right
    f_brand = f("segoeui.ttf", 16)
    bw, bh  = wh(draw, "ClinicSmart SL", f_brand)
    draw.text((width - 46 - bw, height - 34), "ClinicSmart SL", font=f_brand, fill=(75, 100, 97))

    # ── Left editorial panel ──────────────────────────────────────────────────
    ML = 54   # left margin
    
    # Texture
    for y in range(18, height, 28):
        for x in range(ML + 6, SPLIT - 22, 28):
            draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(228, 224, 215))

    # 5-px teal accent strip
    draw.rectangle([0, 0, 5, height], fill=TEAL)

    # ── Headline Logic ────────────────────────────────────────────────────────
    # Use Hook as headline. If no hook, use first sentence of post.
    headline_text = post.get('hook', '').strip()
    if not headline_text:
        # Fallback to truncated post
        body = post.get('post', '')
        headline_text = body.split('.')[0] if body else "DAILY UPDATE"
    
    # Clean up quotes
    headline_text = headline_text.strip('"')
    
    # Uppercase for impact
    headline_text = headline_text.upper()

    f_gs = f("georgiab.ttf", 28)   # sub-serif

    MAX_TXT_W = SPLIT - ML - 40
    
    # Dynamic font sizing for headline
    sz = 100
    f_h = f("bahnschrift.ttf", sz)
    
    # Wrap text
    lines_raw = wrap_text(draw, headline_text, f_h, MAX_TXT_W)
    
    # Shrink if too many lines
    while (len(lines_raw) > 4 or any(wh(draw, l, f_h)[0] > MAX_TXT_W for l in lines_raw)) and sz > 40:
        sz -= 4
        f_h = f("bahnschrift.ttf", sz)
        lines_raw = wrap_text(draw, headline_text, f_h, MAX_TXT_W)
    
    # Limit to 5 lines max to prevent overflow
    lines_raw = lines_raw[:5]

    lh_list = [wh(draw, t, f_h)[1] for t in lines_raw]
    HL_GAP  = 2
    HL_H    = sum(lh_list) + HL_GAP * (len(lines_raw) - 1)

    # Sub-text (Post body snippet)
    sub = post.get('post', '').replace(headline_text, "").strip()
    # Take first 100 chars
    sub = (sub[:100] + "...") if len(sub) > 100 else sub
    sub = sub.replace('\n', ' ')
    
    # Wrap subtext
    sub_lines = wrap_text(draw, sub, f_gs, MAX_TXT_W)
    sub_h = sum(wh(draw, l, f_gs)[1] + 5 for l in sub_lines)
    
    SUB_GAP   = 30

    BLOCK_H   = HL_H + SUB_GAP + sub_h
    block_top = (height - BLOCK_H) // 2 - 12
    
    # Ensure it doesn't start too high
    if block_top < 40: block_top = 40

    cy = block_top
    
    # Draw Headline
    for i, txt in enumerate(lines_raw):
        # Alternate colors for emphasis? Or just INK/TEAL split?
        # Let's make the last line TEAL for impact
        clr = TEAL if i == len(lines_raw) - 1 and len(lines_raw) > 1 else INK
        draw.text((ML, cy), txt, font=f_h, fill=clr)
        cy += lh_list[i] + HL_GAP

    # Accent rule
    rule_y = cy + 14
    draw.rectangle([ML, rule_y, ML + 72, rule_y + 3], fill=TEAL)

    # Draw Sub-text
    cy = rule_y + SUB_GAP
    for l in sub_lines:
        draw.text((ML, cy), l, font=f_gs, fill=DIM)
        cy += wh(draw, l, f_gs)[1] + 5

    # Hashtag bottom-left
    hashtags = post.get('hashtags', [])
    tag_text = hashtags[0] if hashtags else "#ClinicSmartSL"
    f_hash = f("segoeuib.ttf", 16)
    draw.text((ML, height - 34), tag_text, font=f_hash, fill=TEAL)

    # Vertical divider
    draw.line([(SPLIT, 0), (SPLIT, height)], fill=(28, 48, 46), width=1)
    
    return img

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading posts...")
    try:
        posts = json.loads(Path("posts.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("Error: posts.json not found. Run parse_calendar.py first.")
        return

    print(f"Found {len(posts)} posts.")
    
    count = 0
    errors = 0
    
    for post in posts:
        platform = post.get("platform", "Facebook")
        slug = platform.lower()
        day = post.get("day", 1)
        
        # Output directory
        out_dir = BASE_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"day{day:02d}_{slug}.png"
        out_path = out_dir / filename
        
        try:
            img = generate_image(post, platform)
            img.save(out_path)
            # print(f"  Generated {filename}")
            count += 1
        except Exception as e:
            print(f"  Error generating {filename}: {e}")
            errors += 1
            
    print(f"\nDone. Regenerated {count} images with Preview Style.")
    if errors:
        print(f"Errors: {errors}")

if __name__ == "__main__":
    main()
