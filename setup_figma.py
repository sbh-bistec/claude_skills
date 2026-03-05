"""
setup_figma.py
--------------
Verifies your Figma connection, runs the full calendar pipeline,
then tells you exactly how to import the generated images into Figma.

Usage:
    python setup_figma.py

Requirements:
    pip install pillow requests python-dotenv
"""

import os
import sys
import json
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import requests
except ImportError:
    print("✗  'requests' not installed. Run: pip install requests")
    sys.exit(1)


# ── Your Figma file (extracted from the URL you provided) ────────────────────
FIGMA_FILE_KEY = "IOBSNXyeFYvAfBE2tEXllE"
FIGMA_FILE_URL = "https://www.figma.com/design/IOBSNXyeFYvAfBE2tEXllE/irp-d1"


# ── Helpers ───────────────────────────────────────────────────────────────────

def divider(title: str):
    print(f"\n{'─' * 52}")
    print(f"  {title}")
    print(f"{'─' * 52}")


def run_script(script: str) -> bool:
    """Run a Python script and stream its output."""
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,   # stream directly to terminal
    )
    return result.returncode == 0


# ── Step 1: Verify Figma connection ──────────────────────────────────────────

def verify_figma(token: str) -> bool:
    divider("Step 1 — Verify Figma connection")

    headers = {"X-Figma-Token": token}
    url     = f"https://api.figma.com/v1/files/{FIGMA_FILE_KEY}"

    print(f"  Connecting to: {FIGMA_FILE_URL}\n")

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except requests.ConnectionError:
        print("  ✗  No internet connection.")
        return False

    if r.status_code == 200:
        data  = r.json()
        name  = data.get("name", "Unknown")
        pages = data.get("document", {}).get("children", [])

        print(f"  ✓  Connected!")
        print(f"  File name : {name}")
        print(f"  Pages     : {len(pages)}")
        for page in pages:
            frame_count = len(page.get("children", []))
            print(f"    • {page['name']}  ({frame_count} top-level frames)")
        return True

    elif r.status_code == 403:
        print("  ✗  Access denied.")
        print("     Check your FIGMA_TOKEN in the .env file.")
        print("     Make sure the token has access to this file.")
        return False

    elif r.status_code == 404:
        print("  ✗  File not found.")
        print(f"     File key used: {FIGMA_FILE_KEY}")
        return False

    else:
        print(f"  ✗  Unexpected error {r.status_code}: {r.text[:200]}")
        return False


# ── Step 2: Parse calendar ────────────────────────────────────────────────────

def parse_calendar() -> bool:
    divider("Step 2 — Parse SOCIAL-CALENDAR.md")

    if not Path("SOCIAL-CALENDAR.md").exists():
        print("  ✗  SOCIAL-CALENDAR.md not found.")
        print("     Make sure you are running this from the t5/ folder.")
        return False

    return run_script("parse_calendar.py")


# ── Step 3: Generate images ───────────────────────────────────────────────────

def generate_images() -> bool:
    divider("Step 3 — Generate post images")

    if not Path("posts.json").exists():
        print("  ✗  posts.json not found. Step 2 may have failed.")
        return False

    return run_script("generate_posts.py")


# ── Step 4: Figma import instructions ────────────────────────────────────────

def figma_instructions():
    divider("Step 4 — Import images into Figma")

    output_dir  = Path("output")
    png_files   = list(output_dir.rglob("*.png"))
    total       = len(png_files)

    platforms = {
        "linkedin":  len(list((output_dir / "linkedin").glob("*.png")))  if (output_dir / "linkedin").exists()  else 0,
        "facebook":  len(list((output_dir / "facebook").glob("*.png")))  if (output_dir / "facebook").exists()  else 0,
        "instagram": len(list((output_dir / "instagram").glob("*.png"))) if (output_dir / "instagram").exists() else 0,
    }

    abs_output = output_dir.resolve()

    print(f"""
  ✓  {total} images ready:
       LinkedIn  : {platforms['linkedin']} images  → output/linkedin/
       Facebook  : {platforms['facebook']} images  → output/facebook/
       Instagram : {platforms['instagram']} images → output/instagram/

  Output folder:
  {abs_output}

  ─────────────────────────────────────────────────
  HOW TO IMPORT INTO FIGMA  (3 steps)
  ─────────────────────────────────────────────────

  1. Open your Figma file:
     {FIGMA_FILE_URL}

  2. Open your file explorer and go to:
     {abs_output}

  3. Select all images  (Ctrl + A)
     then DRAG them onto the Figma canvas.

     Figma will automatically place each PNG as
     an image frame. You can then arrange them
     by platform (LinkedIn / Facebook / Instagram).

  ─────────────────────────────────────────────────
  TIP: Import one platform at a time to keep things
  organised. Start with output/linkedin/, then
  output/facebook/, then output/instagram/.
  ─────────────────────────────────────────────────
""")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 52)
    print("  Social Media Calendar → Figma Pipeline")
    print("=" * 52)

    # Read token
    token = os.getenv("FIGMA_TOKEN")
    if not token:
        print("""
  ✗  FIGMA_TOKEN not found.

  Fix: Create a file named  .env  in this folder
       with the following content:

       FIGMA_TOKEN=your_token_here

  How to get your token:
    1. Go to figma.com → click your profile (top-left)
    2. Settings → Personal access tokens
    3. Generate new token → copy it
    4. Paste it in the .env file
""")
        sys.exit(1)

    # Run steps
    if not verify_figma(token):
        sys.exit(1)

    if not parse_calendar():
        sys.exit(1)

    if not generate_images():
        sys.exit(1)

    figma_instructions()

    print("=" * 52)
    print("  All done! Open Figma and drag in your images.")
    print("=" * 52 + "\n")


if __name__ == "__main__":
    main()
