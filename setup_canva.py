"""
setup_canva.py
--------------
Connects to Canva via OAuth 2.0 (PKCE), generates social media post images
from SOCIAL-CALENDAR.md, and uploads them to your Canva asset library.

Usage:
    python setup_canva.py

Setup (one-time):
    1. Go to https://www.canva.com/developers
    2. Click "Create an integration" (choose Private)
    3. Under Configuration → Redirect URIs, add:
           http://127.0.0.1:3001/oauth/redirect
    4. Enable scopes: asset:read, asset:write
    5. Copy Client ID and Client Secret
    6. Add to your .env file:
           CANVA_CLIENT_ID=your_client_id
           CANVA_CLIENT_SECRET=your_client_secret

Requirements:
    pip install pillow requests python-dotenv
"""

import os
import sys
import json
import base64
import hashlib
import secrets
import time
import webbrowser
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
from threading import Thread

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


# ── Canva API constants ────────────────────────────────────────────────────────

AUTH_URL     = "https://www.canva.com/api/oauth/authorize"
TOKEN_URL    = "https://api.canva.com/rest/v1/oauth/token"
UPLOAD_URL   = "https://api.canva.com/rest/v1/asset-uploads"
REDIRECT_URI = "http://127.0.0.1:3001/oauth/redirect"
SCOPES       = "asset:read asset:write"


# ── PKCE helpers ───────────────────────────────────────────────────────────────

def generate_pkce():
    """Generate a code_verifier and its SHA-256 code_challenge."""
    verifier  = secrets.token_urlsafe(96)[:128]
    digest    = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


# ── Local OAuth callback server ────────────────────────────────────────────────

_auth_code = None


class _OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        params = parse_qs(urlparse(self.path).query)
        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family:sans-serif;text-align:center;margin-top:60px">
                <h2 style="color:#00c853">&#10003; Connected to Canva!</h2>
                <p>You can close this tab and return to the terminal.</p>
                </body></html>
            """)
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, *args):
        pass  # suppress access logs


def _do_oauth(client_id: str, client_secret: str) -> str:
    """Run the OAuth 2.0 PKCE flow and return an access token."""
    global _auth_code
    _auth_code = None

    verifier, challenge = generate_pkce()
    state = secrets.token_hex(16)

    params = {
        "response_type":         "code",
        "client_id":             client_id,
        "redirect_uri":          REDIRECT_URI,
        "scope":                 SCOPES,
        "state":                 state,
        "code_challenge":        challenge,
        "code_challenge_method": "S256",
    }
    auth_url = AUTH_URL + "?" + urlencode(params)

    # Start the local callback server (handles one request, then stops)
    server = HTTPServer(("127.0.0.1", 3001), _OAuthHandler)
    thread = Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("\n  Opening browser for Canva authorization...")
    print(f"  If the browser doesn't open, visit:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    thread.join(timeout=120)
    server.server_close()

    if not _auth_code:
        print("  ✗  No authorization code received (timed out after 2 minutes).")
        sys.exit(1)

    # Exchange authorization code for access token
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type":    "authorization_code",
            "code":          _auth_code,
            "redirect_uri":  REDIRECT_URI,
            "client_id":     client_id,
            "client_secret": client_secret,
            "code_verifier": verifier,
        },
        timeout=15,
    )

    if resp.status_code != 200:
        print(f"  ✗  Token exchange failed ({resp.status_code}): {resp.text[:300]}")
        sys.exit(1)

    token = resp.json().get("access_token")
    if not token:
        print("  ✗  No access_token in response.")
        sys.exit(1)

    print("  ✓  Authorized successfully!")
    return token


# ── Asset upload ───────────────────────────────────────────────────────────────

def _upload_asset(token: str, path: Path) -> dict | None:
    """Upload a PNG to Canva and poll until complete. Returns asset dict or None."""
    name_b64 = base64.b64encode(path.name.encode()).decode()

    with path.open("rb") as f:
        resp = requests.post(
            UPLOAD_URL,
            headers={
                "Authorization":         f"Bearer {token}",
                "Content-Type":          "application/octet-stream",
                "Asset-Upload-Metadata": json.dumps({"name_base64": name_b64}),
            },
            data=f,
            timeout=60,
        )

    if resp.status_code != 200:
        return None

    job_id = resp.json().get("job", {}).get("id")
    if not job_id:
        return None

    # Poll until the job completes (up to 60 seconds)
    for _ in range(30):
        time.sleep(2)
        poll = requests.get(
            f"{UPLOAD_URL}/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if poll.status_code == 200:
            job = poll.json().get("job", {})
            status = job.get("status")
            if status == "success":
                return job.get("asset")
            elif status == "failed":
                return None

    return None  # timed out


# ── Pipeline helpers ───────────────────────────────────────────────────────────

def _divider(title: str):
    print(f"\n{'─' * 52}")
    print(f"  {title}")
    print(f"{'─' * 52}")


def _run_script(script: str) -> bool:
    result = subprocess.run([sys.executable, script], capture_output=False)
    return result.returncode == 0


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 52)
    print("  Social Media Calendar → Canva Pipeline")
    print("=" * 52)

    # ── Step 1: Load credentials ──────────────────────────────────────────────
    _divider("Step 1 — Load Canva credentials")

    client_id     = os.getenv("CANVA_CLIENT_ID")
    client_secret = os.getenv("CANVA_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("""
  ✗  Canva credentials not found in .env

  Fix:
    1. Go to https://www.canva.com/developers
    2. Click "Create an integration"  →  choose Private
    3. Under Configuration → Redirect URIs, add:
           http://127.0.0.1:3001/oauth/redirect
    4. Enable scopes: asset:read  and  asset:write
    5. Copy your Client ID and Client Secret
    6. Add these lines to your .env file:

           CANVA_CLIENT_ID=your_client_id_here
           CANVA_CLIENT_SECRET=your_client_secret_here

    Then run this script again.
""")
        sys.exit(1)

    print("  ✓  Credentials found.")

    # ── Step 2: OAuth ─────────────────────────────────────────────────────────
    _divider("Step 2 — Authorize with Canva (OAuth 2.0)")
    token = _do_oauth(client_id, client_secret)

    # ── Step 3: Parse calendar ────────────────────────────────────────────────
    if not Path("posts.json").exists():
        _divider("Step 3 — Parse SOCIAL-CALENDAR.md")
        if not Path("SOCIAL-CALENDAR.md").exists():
            print("  ✗  SOCIAL-CALENDAR.md not found.")
            sys.exit(1)
        if not _run_script("parse_calendar.py"):
            print("  ✗  parse_calendar.py failed.")
            sys.exit(1)
    else:
        print("\n  ✓  posts.json already exists — skipping parse step.")

    # ── Step 4: Generate images ───────────────────────────────────────────────
    output_dir    = Path("output")
    existing_pngs = list(output_dir.rglob("*.png")) if output_dir.exists() else []

    if not existing_pngs:
        _divider("Step 4 — Generate post images")
        if not Path("posts.json").exists():
            print("  ✗  posts.json missing — cannot generate images.")
            sys.exit(1)
        if not _run_script("generate_posts.py"):
            print("  ✗  generate_posts.py failed.")
            sys.exit(1)
    else:
        print(f"\n  ✓  Found {len(existing_pngs)} existing images — skipping generation.")

    # ── Step 5: Upload to Canva ───────────────────────────────────────────────
    _divider("Step 5 — Upload images to Canva")

    png_files = sorted(output_dir.rglob("*.png"))
    total     = len(png_files)

    if total == 0:
        print("  ✗  No PNG files found in output/")
        sys.exit(1)

    print(f"  Uploading {total} images to your Canva asset library...\n")

    success   = 0
    failed    = 0
    asset_ids = []

    for i, path in enumerate(png_files, 1):
        relative = path.relative_to(output_dir)
        print(f"  [{i:02d}/{total}] {relative} ", end="", flush=True)

        asset = _upload_asset(token, path)
        if asset:
            asset_id = asset.get("id", "?")
            asset_ids.append(asset_id)
            print(f"✓  (asset id: {asset_id})")
            success += 1
        else:
            print("✗  (upload failed)")
            failed += 1

    # ── Step 6: Summary ───────────────────────────────────────────────────────
    _divider("Step 6 — Done!")

    platforms = {
        "LinkedIn":  len(list((output_dir / "linkedin").glob("*.png")))  if (output_dir / "linkedin").exists()  else 0,
        "Facebook":  len(list((output_dir / "facebook").glob("*.png")))  if (output_dir / "facebook").exists()  else 0,
        "Instagram": len(list((output_dir / "instagram").glob("*.png"))) if (output_dir / "instagram").exists() else 0,
    }

    print(f"""
  ✓  {success} of {total} images uploaded to Canva!
  {"✗  " + str(failed) + " images failed." if failed else ""}

  Breakdown:
    LinkedIn  : {platforms['LinkedIn']} images
    Facebook  : {platforms['Facebook']} images
    Instagram : {platforms['Instagram']} images

  ─────────────────────────────────────────────────
  HOW TO USE YOUR IMAGES IN CANVA
  ─────────────────────────────────────────────────

  1. Open https://www.canva.com
  2. Click "Create a design" → choose the post size
     (e.g. "Instagram Post", "Facebook Post", "LinkedIn Post")
  3. In the left panel, click "Uploads"
  4. Your images will appear there — click to add them
     to your design

  TIP: Search by platform name (linkedin / facebook /
  instagram) to quickly filter your uploads.
  ─────────────────────────────────────────────────
""")

    print("=" * 52 + "\n")


if __name__ == "__main__":
    main()
