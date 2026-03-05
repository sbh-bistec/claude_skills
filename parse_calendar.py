"""
parse_calendar.py
-----------------
Parses SOCIAL-CALENDAR.md into structured posts.json.

Usage:
    python parse_calendar.py
Output:
    posts.json  — list of post objects, one per platform per day
"""

import re
import json
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_markdown(text: str) -> str:
    """Strip common markdown formatting for plain-text rendering."""
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)       # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)            # *italic*
    text = re.sub(r'`([^`]+)`', r'\1', text)              # `code`
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [link](url)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # headings
    text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)  # bullets
    text = re.sub(r'\n{3,}', '\n\n', text)                # collapse blank lines
    return text.strip()


def extract_field(content: str, field: str) -> str:
    """
    Extract a markdown field block like:
        **Hook:**
        "some text..."

        **Post:**
        paragraph text...

    Stops at the next **Field:** marker or end of string.
    """
    pattern = rf'\*\*{field}:\*\*\s*\n([\s\S]+?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)'
    m = re.search(pattern, content)
    if m:
        return clean_markdown(m.group(1))
    return ""


# ── Core parser ───────────────────────────────────────────────────────────────

def parse_calendar(filepath: str = "SOCIAL-CALENDAR.md") -> list[dict]:
    text = Path(filepath).read_text(encoding="utf-8")
    posts = []

    # ── Split into day blocks ────────────────────────────────────────────────
    # Each block starts with: #### DAY X — Weekday, April N (optional holiday)
    day_blocks = re.split(r'\n(?=#### DAY \d+)', text)

    for block in day_blocks:
        day_header = re.match(
            r'#### DAY (\d+) — (\w+), April (\d+)(.*?)$',
            block, re.MULTILINE
        )
        if not day_header:
            continue

        day_num  = int(day_header.group(1))
        weekday  = day_header.group(2)
        date_num = day_header.group(3)
        holiday  = day_header.group(4).strip().strip('*').strip('(').strip(')')

        date_label = f"{weekday}, April {date_num}"
        if holiday:
            date_label += f"  {holiday}"

        # ── Pillar ──────────────────────────────────────────────────────────
        pillar_m = re.search(r'\*\*\[PILLAR:\s*([^\]]+)\]\*\*', block)
        pillar   = pillar_m.group(1).strip() if pillar_m else "General"

        # Normalise pillar to base type (strip subtext after "—")
        pillar_base = pillar.split("—")[0].strip()

        # ── Split block by platform headers ─────────────────────────────────
        # Each platform section starts with: **LinkedIn**, **Facebook**, **Instagram**
        platform_parts = re.split(
            r'\n(?=\*\*(?:LinkedIn|Facebook|Instagram)\*\*)',
            block
        )

        for part in platform_parts:
            plat_m = re.match(
                r'\*\*(LinkedIn|Facebook|Instagram)\*\*\s*\|?\s*(.*?)$',
                part, re.MULTILINE
            )
            if not plat_m:
                continue

            platform  = plat_m.group(1)
            meta_line = plat_m.group(2).strip()

            # Time
            time_m = re.search(r'(\d{1,2}:\d{2} [AP]M)', meta_line)
            time   = time_m.group(1) if time_m else ""

            # Post type from meta  e.g. "Text Post | 9:00 AM"
            post_type = ""
            type_m = re.search(r'\*\*Type:\*\*\s*([^\n]+)', part)
            if type_m:
                post_type = type_m.group(1).strip()
            elif "|" in meta_line:
                # fallback: first segment before "|" or time
                segments = [s.strip() for s in meta_line.split("|")]
                post_type = segments[0] if segments[0] and not re.match(r'\d', segments[0]) else ""

            # Hook
            hook = ""
            hook_m = re.search(r'\*\*Hook:\*\*\s*\n"([^"]+)"', part)
            if hook_m:
                hook = hook_m.group(1).strip()

            # Post body  (LinkedIn/Facebook)
            post_text = extract_field(part, "Post")

            # Caption fallback (Instagram / holiday posts)
            if not post_text:
                post_text = extract_field(part, "Caption")

            # Tweet fallback
            if not post_text:
                post_text = extract_field(part, "Tweet")

            # Visual direction (Instagram carousels/reels)
            visual = extract_field(part, "Visual Direction")

            # Slide content (carousel slides)
            slides = []
            slide_matches = re.findall(r'- \*\*Slide \d+:\*\*\s*"([^"]+)"', part)
            if slide_matches:
                slides = slide_matches

            # Hashtags
            hashtags = []
            hash_m = re.search(r'\*\*Hashtags:\*\*\s*`([^`]+)`', part)
            if hash_m:
                hashtags = re.findall(r'#\w+', hash_m.group(1))

            if post_text or hook:
                posts.append({
                    "day":      day_num,
                    "date":     date_label,
                    "pillar":   pillar_base,
                    "platform": platform,
                    "time":     time,
                    "type":     post_type,
                    "hook":     hook,
                    "post":     post_text,
                    "hashtags": hashtags,
                    "visual":   visual,
                    "slides":   slides,
                })

    return posts


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    posts = parse_calendar()

    out = Path("posts.json")
    out.write_text(
        json.dumps(posts, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    from collections import Counter
    platforms = Counter(p["platform"] for p in posts)
    pillars   = Counter(p["pillar"]   for p in posts)

    print(f"\n✓ Parsed {len(posts)} posts  →  posts.json\n")
    print("By platform:")
    for k, v in sorted(platforms.items()):
        print(f"  {k:<12} {v} posts")
    print("\nBy pillar:")
    for k, v in sorted(pillars.items()):
        print(f"  {k:<25} {v} posts")
