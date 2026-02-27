"""
BMAD Beginner's Guide — Multi-page PDF Presentation
Design Philosophy: Systematic Convergence
"""

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import math
import os

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

W, H = landscape(A4)  # 841.89 x 595.28
FONT_DIR = os.path.join(os.path.dirname(__file__), ".claude", "skills", "canvas-design", "canvas-fonts")
OUTPUT = os.path.join(os.path.dirname(__file__), "BMAD_Beginners_Guide.pdf")

# ─── COLOR PALETTE: Systematic Convergence ────────────────────────────────────

SLATE_DARK    = HexColor("#1B2838")
SLATE_MID     = HexColor("#2D3E50")
SLATE_LIGHT   = HexColor("#4A6274")
IVORY         = HexColor("#F5F0E8")
IVORY_WARM    = HexColor("#EDE6D8")
INDIGO        = HexColor("#2C3E7B")
INDIGO_DEEP   = HexColor("#1A2555")
TEAL          = HexColor("#1A8A7D")
TEAL_LIGHT    = HexColor("#2ABFAE")
AMBER         = HexColor("#D4920B")
AMBER_SOFT    = HexColor("#E8B44C")
WHITE         = HexColor("#FFFFFF")
WHITE_TRANS   = Color(1, 1, 1, 0.08)
WHITE_TRANS2  = Color(1, 1, 1, 0.04)
TEAL_TRANS    = Color(0.10, 0.54, 0.49, 0.15)
INDIGO_TRANS  = Color(0.17, 0.24, 0.48, 0.10)
DARK_OVERLAY  = Color(0.106, 0.157, 0.220, 0.6)


# ─── FONT REGISTRATION (Windows System Fonts) ────────────────────────────────

WINFONTS = os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts')

def register_fonts():
    fonts = {
        # Display / Title — Impact for bold headlines
        "BigShoulders-Bold": "impact.ttf",
        "BigShoulders": "trebuc.ttf",
        # Body — Calibri family
        "WorkSans": "calibri.ttf",
        "WorkSans-Bold": "calibrib.ttf",
        "WorkSans-Italic": "calibrii.ttf",
        # Mono — Consolas
        "DMMono": "consola.ttf",
        "GeistMono": "consola.ttf",
        "GeistMono-Bold": "consolab.ttf",
        "IBMPlexMono": "consola.ttf",
        "IBMPlexMono-Bold": "consolab.ttf",
        # Light / Subtitle — Segoe UI Light
        "Jura-Light": "segoeuil.ttf",
        "Jura-Medium": "segoeui.ttf",
        # Sans — Segoe UI family
        "InstrumentSans": "segoeui.ttf",
        "InstrumentSans-Bold": "segoeuib.ttf",
        # Serif / Italic — Georgia
        "InstrumentSerif": "georgia.ttf",
        "InstrumentSerif-Italic": "georgiai.ttf",
    }
    for name, filename in fonts.items():
        path = os.path.join(WINFONTS, filename)
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception:
                pass

register_fonts()


# ─── HELPER DRAWING FUNCTIONS ────────────────────────────────────────────────

def draw_grid_pattern(c, x0, y0, w, h, spacing=30, color=WHITE_TRANS):
    """Draw subtle grid lines as background texture."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(0.3)
    for x in range(int(x0), int(x0 + w), spacing):
        c.line(x, y0, x, y0 + h)
    for y in range(int(y0), int(y0 + h), spacing):
        c.line(x0, y, x0 + w, y)
    c.restoreState()


def draw_dot_grid(c, x0, y0, w, h, spacing=24, radius=0.8, color=WHITE_TRANS):
    """Draw subtle dot grid pattern."""
    c.saveState()
    c.setFillColor(color)
    for x in range(int(x0), int(x0 + w), spacing):
        for y in range(int(y0), int(y0 + h), spacing):
            c.circle(x, y, radius, fill=1, stroke=0)
    c.restoreState()


def draw_connection_line(c, x1, y1, x2, y2, color=TEAL_LIGHT, width=1.5):
    """Draw a flowing connection line between two points."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.setLineCap(1)
    mx = (x1 + x2) / 2
    p = c.beginPath()
    p.moveTo(x1, y1)
    p.curveTo(mx, y1, mx, y2, x2, y2)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def draw_node_circle(c, x, y, r, fill_color=TEAL, stroke_color=None, stroke_w=1.5):
    """Draw a filled circle node."""
    c.saveState()
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_w)
        c.circle(x, y, r, fill=1, stroke=1)
    else:
        c.circle(x, y, r, fill=1, stroke=0)
    c.restoreState()


def draw_rounded_rect(c, x, y, w, h, r=8, fill_color=None, stroke_color=None, stroke_w=1):
    """Draw a rounded rectangle."""
    c.saveState()
    if fill_color:
        c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_w)
    c.roundRect(x, y, w, h, r, fill=1 if fill_color else 0, stroke=1 if stroke_color else 0)
    c.restoreState()


def draw_decorative_lines(c, x, y, count=5, length=60, spacing=6, color=WHITE_TRANS):
    """Draw horizontal decorative line cluster."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(0.5)
    for i in range(count):
        c.line(x, y + i * spacing, x + length, y + i * spacing)
    c.restoreState()


def draw_corner_marks(c, margin=40, size=20, color=TEAL):
    """Draw registration-style corner marks."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(0.6)
    # Top-left
    c.line(margin, H - margin, margin + size, H - margin)
    c.line(margin, H - margin, margin, H - margin - size)
    # Top-right
    c.line(W - margin, H - margin, W - margin - size, H - margin)
    c.line(W - margin, H - margin, W - margin, H - margin - size)
    # Bottom-left
    c.line(margin, margin, margin + size, margin)
    c.line(margin, margin, margin, margin + size)
    # Bottom-right
    c.line(W - margin, margin, W - margin - size, margin)
    c.line(W - margin, margin, W - margin, margin + size)
    c.restoreState()


def draw_page_number(c, num, total):
    """Draw minimal page indicator."""
    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.35))
    c.setFont("DMMono", 7)
    c.drawRightString(W - 50, 32, f"{num:02d} / {total:02d}")
    c.restoreState()


def draw_section_marker(c, label, y=H - 55):
    """Draw top-left section classification marker."""
    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.3))
    c.setFont("DMMono", 6.5)
    c.drawString(50, y, label.upper())
    c.restoreState()


def centered_text(c, text, y, font="WorkSans", size=12, color=IVORY):
    """Draw centered text."""
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(W / 2, y, text)
    c.restoreState()


def draw_horizontal_rule(c, y, x1=None, x2=None, color=TEAL, width=0.6):
    """Draw a subtle horizontal rule."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1 or 100, y, x2 or W - 100, y)
    c.restoreState()


# ─── BACKGROUND ──────────────────────────────────────────────────────────────

def draw_base_background(c, primary=SLATE_DARK, secondary=SLATE_MID):
    """Draw the foundational dark background with subtle gradient feel."""
    # Base fill
    c.setFillColor(primary)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # Subtle overlay rectangles for depth
    c.setFillColor(Color(0.17, 0.24, 0.31, 0.3))
    c.rect(0, 0, W, H * 0.4, fill=1, stroke=0)
    c.setFillColor(Color(0.10, 0.15, 0.22, 0.2))
    c.rect(0, H * 0.7, W, H * 0.3, fill=1, stroke=0)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1: COVER
# ═════════════════════════════════════════════════════════════════════════════

def page_cover(c):
    draw_base_background(c)

    # Geometric background pattern — convergent diagonal lines
    c.saveState()
    c.setStrokeColor(Color(1, 1, 1, 0.03))
    c.setLineWidth(0.4)
    cx, cy = W / 2, H / 2
    for angle in range(0, 360, 8):
        rad = math.radians(angle)
        x2 = cx + 600 * math.cos(rad)
        y2 = cy + 600 * math.sin(rad)
        c.line(cx, cy, x2, y2)
    c.restoreState()

    # Concentric circles radiating from center
    c.saveState()
    for r in range(40, 320, 35):
        alpha = max(0.01, 0.06 - r * 0.0002)
        c.setStrokeColor(Color(0.16, 0.68, 0.62, alpha))
        c.setLineWidth(0.5)
        c.circle(cx, cy, r, fill=0, stroke=1)
    c.restoreState()

    # Dot grid — very subtle
    draw_dot_grid(c, 50, 50, W - 100, H - 100, spacing=40, radius=0.5, color=Color(1, 1, 1, 0.025))

    # Corner marks
    draw_corner_marks(c, margin=35, size=18, color=Color(0.16, 0.75, 0.68, 0.5))

    # Central node
    draw_node_circle(c, cx, cy, 6, fill_color=TEAL_LIGHT)

    # ─── TITLE BLOCK ──────────────────────────────────────────────────────
    # "BMAD" massive display
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("BigShoulders-Bold", 130)
    c.drawCentredString(cx, cy + 50, "BMAD")
    c.restoreState()

    # Thin rule under title
    draw_horizontal_rule(c, cy + 40, cx - 180, cx + 180, color=Color(0.16, 0.75, 0.68, 0.6), width=0.8)

    # Subtitle
    c.saveState()
    c.setFillColor(Color(0.96, 0.94, 0.91, 0.75))
    c.setFont("Jura-Light", 13.5)
    c.drawCentredString(cx, cy + 10, "Breakthrough Method for Agile AI-Driven Development")
    c.restoreState()

    # Secondary subtitle
    c.saveState()
    c.setFillColor(TEAL_LIGHT)
    c.setFont("InstrumentSans", 10)
    c.drawCentredString(cx, cy - 18, "A   B E G I N N E R ' S   G U I D E")
    c.restoreState()

    # Bottom classification
    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.2))
    c.setFont("DMMono", 6.5)
    c.drawCentredString(cx, 50, "SYSTEMATIC CONVERGENCE  //  2026  //  OPEN SOURCE  //  MIT LICENSE")
    c.restoreState()

    draw_page_number(c, 1, 8)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2: WHAT IS BMAD?
# ═════════════════════════════════════════════════════════════════════════════

def page_what_is_bmad(c):
    draw_base_background(c)
    draw_dot_grid(c, 50, 50, W - 100, H - 100, spacing=36, radius=0.4, color=Color(1, 1, 1, 0.02))
    draw_corner_marks(c, margin=35, size=18, color=Color(0.16, 0.75, 0.68, 0.3))
    draw_section_marker(c, "Section 01  —  Overview")

    cx = W / 2

    # Left vertical accent line
    c.saveState()
    c.setStrokeColor(TEAL)
    c.setLineWidth(2.5)
    c.line(80, 100, 80, H - 80)
    c.restoreState()

    # Title
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("BigShoulders-Bold", 52)
    c.drawString(110, H - 120, "What is BMAD?")
    c.restoreState()

    # Thin separator
    draw_horizontal_rule(c, H - 140, 110, 460, TEAL_LIGHT, 0.6)

    # Tagline
    c.saveState()
    c.setFillColor(TEAL_LIGHT)
    c.setFont("InstrumentSerif-Italic", 16)
    c.drawString(110, H - 172, "From chaos to clarity in AI-driven development.")
    c.restoreState()

    # Description blocks — left column
    desc_lines = [
        ("An open-source, multi-agent framework", "WorkSans", 12, IVORY),
        ("that structures AI-assisted software development", "WorkSans", 12, IVORY),
        ("into a systematic, repeatable process.", "WorkSans", 12, IVORY),
    ]
    yy = H - 220
    for text, font, size, color in desc_lines:
        c.saveState()
        c.setFillColor(color)
        c.setFont(font, size)
        c.drawString(110, yy, text)
        c.restoreState()
        yy -= 22

    # Creator credit
    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.4))
    c.setFont("DMMono", 8)
    c.drawString(110, yy - 15, "CREATED BY ADAM BLACKINGTON  //  MIT LICENSE  //  100% FREE")
    c.restoreState()

    # ─── RIGHT SIDE: Visual diagram of multi-agent concept ────────────────
    rx = 580
    ry = H / 2 + 30

    # Central hub
    draw_node_circle(c, rx, ry, 30, fill_color=Color(0.10, 0.54, 0.49, 0.25), stroke_color=TEAL_LIGHT, stroke_w=1.5)
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("GeistMono-Bold", 8)
    c.drawCentredString(rx, ry - 3, "BMAD")
    c.restoreState()

    # Satellite agent nodes
    agents = [
        ("Analyst", -55),
        ("PM", -15),
        ("Architect", 25),
        ("PO", 65),
        ("SM", 105),
        ("Dev", 145),
        ("QA", 185),
    ]
    for i, (label, angle_offset) in enumerate(agents):
        angle = math.radians(90 + angle_offset * 1.0)
        dist = 100
        ax = rx + dist * math.cos(angle)
        ay = ry + dist * math.sin(angle)
        # Connection line
        draw_connection_line(c, rx, ry, ax, ay, color=Color(0.16, 0.75, 0.68, 0.3), width=0.7)
        # Node
        node_color = TEAL if i < 4 else INDIGO
        draw_node_circle(c, ax, ay, 16, fill_color=Color(node_color.red, node_color.green, node_color.blue, 0.35), stroke_color=Color(1,1,1,0.2), stroke_w=0.5)
        c.saveState()
        c.setFillColor(IVORY)
        c.setFont("DMMono", 6)
        c.drawCentredString(ax, ay - 2.5, label.upper())
        c.restoreState()

    # Labels for groups
    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.3))
    c.setFont("DMMono", 6)
    c.drawCentredString(rx, ry - 155, "SPECIALIZED AI AGENTS WITH DISTINCT ROLES")
    c.restoreState()

    # Bottom decorative element
    draw_decorative_lines(c, 110, 80, count=3, length=120, spacing=4, color=Color(1,1,1,0.06))

    draw_page_number(c, 2, 8)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3: CORE PRINCIPLES
# ═════════════════════════════════════════════════════════════════════════════

def page_core_principles(c):
    draw_base_background(c, SLATE_DARK, SLATE_MID)
    draw_grid_pattern(c, 0, 0, W, H, spacing=50, color=Color(1, 1, 1, 0.015))
    draw_corner_marks(c, margin=35, size=18, color=Color(0.16, 0.75, 0.68, 0.3))
    draw_section_marker(c, "Section 02  —  Foundations")

    # Title
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("BigShoulders-Bold", 48)
    c.drawString(80, H - 110, "3 Core Principles")
    c.restoreState()

    draw_horizontal_rule(c, H - 128, 80, 400, TEAL_LIGHT, 0.5)

    # ─── Three principle cards ────────────────────────────────────────────
    cards = [
        {
            "num": "01",
            "title": "Documentation as",
            "title2": "Source of Truth",
            "body": "Docs drive everything downstream.",
            "body2": "Code is a derivative artifact.",
            "icon_type": "doc",
        },
        {
            "num": "02",
            "title": "Agent-as-Code",
            "title2": "",
            "body": "AI agents defined as version-",
            "body2": "controlled Markdown files.",
            "icon_type": "code",
        },
        {
            "num": "03",
            "title": "Structured",
            "title2": "Handoffs",
            "body": "Explicit artifacts prevent",
            "body2": "context loss between agents.",
            "icon_type": "handoff",
        },
    ]

    card_w = 210
    card_h = 260
    gap = 30
    total_w = 3 * card_w + 2 * gap
    start_x = (W - total_w) / 2
    card_y = 80

    for i, card in enumerate(cards):
        x = start_x + i * (card_w + gap)
        y = card_y

        # Card background
        draw_rounded_rect(c, x, y, card_w, card_h, r=4,
                          fill_color=Color(1, 1, 1, 0.04),
                          stroke_color=Color(1, 1, 1, 0.08), stroke_w=0.5)

        # Top accent line
        c.saveState()
        colors = [TEAL, INDIGO, AMBER]
        c.setFillColor(colors[i])
        c.rect(x, y + card_h - 3, card_w, 3, fill=1, stroke=0)
        c.restoreState()

        # Number
        c.saveState()
        c.setFillColor(colors[i])
        c.setFont("BigShoulders-Bold", 36)
        c.drawString(x + 20, y + card_h - 60, card["num"])
        c.restoreState()

        # Icon area — abstract geometric
        ix = x + card_w - 50
        iy = y + card_h - 55
        c.saveState()
        if card["icon_type"] == "doc":
            c.setStrokeColor(Color(0.16, 0.75, 0.68, 0.4))
            c.setLineWidth(0.7)
            c.rect(ix, iy, 18, 24, fill=0, stroke=1)
            for ln in range(4):
                c.line(ix + 3, iy + 18 - ln * 5, ix + 15, iy + 18 - ln * 5)
        elif card["icon_type"] == "code":
            c.setStrokeColor(Color(0.17, 0.24, 0.48, 0.6))
            c.setLineWidth(0.8)
            c.line(ix, iy + 12, ix + 7, iy + 20)
            c.line(ix, iy + 12, ix + 7, iy + 4)
            c.line(ix + 18, iy + 12, ix + 11, iy + 20)
            c.line(ix + 18, iy + 12, ix + 11, iy + 4)
        else:
            c.setStrokeColor(Color(0.83, 0.57, 0.04, 0.5))
            c.setLineWidth(0.8)
            c.circle(ix + 4, iy + 12, 6, fill=0, stroke=1)
            c.line(ix + 10, iy + 12, ix + 14, iy + 12)
            c.circle(ix + 20, iy + 12, 6, fill=0, stroke=1)
        c.restoreState()

        # Title
        c.saveState()
        c.setFillColor(IVORY)
        c.setFont("InstrumentSans-Bold", 15)
        c.drawString(x + 20, y + card_h - 105, card["title"])
        if card["title2"]:
            c.drawString(x + 20, y + card_h - 124, card["title2"])
        c.restoreState()

        # Thin separator inside card
        sep_y = y + card_h - 140
        c.saveState()
        c.setStrokeColor(Color(1, 1, 1, 0.1))
        c.setLineWidth(0.4)
        c.line(x + 20, sep_y, x + card_w - 20, sep_y)
        c.restoreState()

        # Body text
        c.saveState()
        c.setFillColor(Color(1, 1, 1, 0.6))
        c.setFont("WorkSans", 10)
        c.drawString(x + 20, sep_y - 22, card["body"])
        c.drawString(x + 20, sep_y - 38, card["body2"])
        c.restoreState()

    draw_page_number(c, 3, 8)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4: THE 4 PHASES
# ═════════════════════════════════════════════════════════════════════════════

def page_four_phases(c):
    draw_base_background(c)
    draw_dot_grid(c, 50, 50, W - 100, H - 100, spacing=40, radius=0.35, color=Color(1, 1, 1, 0.018))
    draw_corner_marks(c, margin=35, size=18, color=Color(0.16, 0.75, 0.68, 0.3))
    draw_section_marker(c, "Section 03  —  Lifecycle")

    # Title
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("BigShoulders-Bold", 48)
    c.drawString(80, H - 110, "The 4 Phases")
    c.restoreState()

    draw_horizontal_rule(c, H - 128, 80, 340, TEAL_LIGHT, 0.5)

    # Subtitle
    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.4))
    c.setFont("Jura-Light", 10)
    c.drawString(80, H - 150, "A SYSTEMATIC CYCLE FROM IDEA TO IMPLEMENTATION")
    c.restoreState()

    # ─── Phase flow — horizontal layout with connecting arrows ────────────
    phases = [
        {"num": "01", "name": "Analysis", "output": "Project Brief", "color": TEAL},
        {"num": "02", "name": "Planning", "output": "PRD + Architecture", "color": INDIGO},
        {"num": "03", "name": "Solutioning", "output": "Alignment + Stories", "color": AMBER},
        {"num": "04", "name": "Implementation", "output": "Code + QA", "color": TEAL_LIGHT},
    ]

    phase_w = 155
    phase_h = 180
    gap = 22
    arrow_len = gap
    total_w = 4 * phase_w + 3 * gap
    sx = (W - total_w) / 2
    sy = 120

    for i, phase in enumerate(phases):
        x = sx + i * (phase_w + gap)
        y = sy

        # Phase box
        draw_rounded_rect(c, x, y, phase_w, phase_h, r=3,
                          fill_color=Color(1, 1, 1, 0.035),
                          stroke_color=Color(1, 1, 1, 0.07), stroke_w=0.5)

        # Top colored bar
        c.saveState()
        c.setFillColor(phase["color"])
        c.rect(x, y + phase_h - 3, phase_w, 3, fill=1, stroke=0)
        c.restoreState()

        # Large number
        c.saveState()
        c.setFillColor(Color(phase["color"].red, phase["color"].green, phase["color"].blue, 0.2))
        c.setFont("BigShoulders-Bold", 60)
        c.drawString(x + 12, y + phase_h - 80, phase["num"])
        c.restoreState()

        # Phase name
        c.saveState()
        c.setFillColor(IVORY)
        c.setFont("InstrumentSans-Bold", 16)
        c.drawString(x + 15, y + 65, phase["name"])
        c.restoreState()

        # Separator
        c.saveState()
        c.setStrokeColor(Color(1, 1, 1, 0.1))
        c.setLineWidth(0.3)
        c.line(x + 15, y + 55, x + phase_w - 15, y + 55)
        c.restoreState()

        # Output label
        c.saveState()
        c.setFillColor(Color(1, 1, 1, 0.45))
        c.setFont("DMMono", 7.5)
        c.drawString(x + 15, y + 35, "OUTPUT:")
        c.setFillColor(phase["color"])
        c.setFont("DMMono", 7.5)
        c.drawString(x + 15, y + 20, phase["output"])
        c.restoreState()

        # Arrow to next phase
        if i < 3:
            ax1 = x + phase_w + 2
            ax2 = x + phase_w + gap - 2
            ay = y + phase_h / 2
            c.saveState()
            c.setStrokeColor(Color(1, 1, 1, 0.25))
            c.setLineWidth(1)
            c.setLineCap(1)
            c.line(ax1, ay, ax2, ay)
            # Arrowhead
            c.line(ax2 - 5, ay + 4, ax2, ay)
            c.line(ax2 - 5, ay - 4, ax2, ay)
            c.restoreState()

    # Bottom cycling arrow hint
    c.saveState()
    c.setStrokeColor(Color(0.16, 0.75, 0.68, 0.15))
    c.setLineWidth(0.8)
    c.setDash([4, 4])
    p = c.beginPath()
    # Arc under all phases
    end_x = sx + total_w
    p.moveTo(end_x - 20, sy - 10)
    p.curveTo(end_x - 100, sy - 45, sx + 100, sy - 45, sx + 20, sy - 10)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.2))
    c.setFont("DMMono", 6)
    c.drawCentredString(W / 2, sy - 48, "CONTINUOUS CYCLE")
    c.restoreState()

    draw_page_number(c, 4, 8)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5: THE 7 AGENT ROLES
# ═════════════════════════════════════════════════════════════════════════════

def page_agent_roles(c):
    draw_base_background(c, SLATE_DARK, SLATE_MID)
    draw_grid_pattern(c, 0, 0, W, H, spacing=60, color=Color(1, 1, 1, 0.012))
    draw_corner_marks(c, margin=35, size=18, color=Color(0.16, 0.75, 0.68, 0.3))
    draw_section_marker(c, "Section 04  —  Agents")

    cx = W / 2

    # Title
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("BigShoulders-Bold", 48)
    c.drawCentredString(cx, H - 100, "The 7 Agent Roles")
    c.restoreState()

    draw_horizontal_rule(c, H - 118, cx - 180, cx + 180, TEAL_LIGHT, 0.5)

    # ─── Two groups ───────────────────────────────────────────────────────

    # PLANNING AGENTS (left)
    plan_x = 90
    group_y = H - 165

    c.saveState()
    c.setFillColor(TEAL)
    c.setFont("DMMono", 8)
    c.drawString(plan_x, group_y, "PLANNING AGENTS")
    c.restoreState()

    planning_agents = [
        ("Analyst", "Explores idea space, surfaces constraints,", "produces the project brief."),
        ("Product Manager", "Turns brief into PRD with requirements,", "epics, and user stories."),
        ("Architect", "Designs full-stack system architecture,", "component maps, and data flow."),
        ("Product Owner", "Aligns all documents, resolves conflicts,", "runs the master checklist."),
    ]

    card_w = 310
    card_h = 72
    yy = group_y - 35

    for agent_name, line1, line2 in planning_agents:
        # Card
        draw_rounded_rect(c, plan_x, yy - card_h + 15, card_w, card_h, r=3,
                          fill_color=Color(1, 1, 1, 0.03),
                          stroke_color=Color(1, 1, 1, 0.06), stroke_w=0.4)
        # Left accent
        c.saveState()
        c.setFillColor(TEAL)
        c.rect(plan_x, yy - card_h + 15, 3, card_h, fill=1, stroke=0)
        c.restoreState()

        # Node dot
        draw_node_circle(c, plan_x + 20, yy - 10, 5, fill_color=Color(0.16, 0.75, 0.68, 0.5))

        # Agent name
        c.saveState()
        c.setFillColor(IVORY)
        c.setFont("InstrumentSans-Bold", 12)
        c.drawString(plan_x + 35, yy - 6, agent_name)
        c.restoreState()

        # Description
        c.saveState()
        c.setFillColor(Color(1, 1, 1, 0.45))
        c.setFont("WorkSans", 8.5)
        c.drawString(plan_x + 35, yy - 24, line1)
        c.drawString(plan_x + 35, yy - 37, line2)
        c.restoreState()

        yy -= card_h + 8

    # EXECUTION AGENTS (right)
    exec_x = 460
    group_y2 = H - 165

    c.saveState()
    c.setFillColor(INDIGO)
    c.setFont("DMMono", 8)
    c.drawString(exec_x, group_y2, "EXECUTION AGENTS")
    c.restoreState()

    execution_agents = [
        ("Scrum Master", "Drafts hyper-detailed stories with", "embedded context and acceptance criteria."),
        ("Developer", "Implements stories with tests on a", "branch, guided by control manifest."),
        ("QA Agent", "Reviews stories, designs test cases,", "assesses non-functional requirements."),
    ]

    yy2 = group_y2 - 35

    for agent_name, line1, line2 in execution_agents:
        draw_rounded_rect(c, exec_x, yy2 - card_h + 15, card_w, card_h, r=3,
                          fill_color=Color(1, 1, 1, 0.03),
                          stroke_color=Color(1, 1, 1, 0.06), stroke_w=0.4)
        # Left accent
        c.saveState()
        c.setFillColor(INDIGO)
        c.rect(exec_x, yy2 - card_h + 15, 3, card_h, fill=1, stroke=0)
        c.restoreState()

        draw_node_circle(c, exec_x + 20, yy2 - 10, 5, fill_color=Color(0.17, 0.24, 0.48, 0.6))

        c.saveState()
        c.setFillColor(IVORY)
        c.setFont("InstrumentSans-Bold", 12)
        c.drawString(exec_x + 35, yy2 - 6, agent_name)
        c.restoreState()

        c.saveState()
        c.setFillColor(Color(1, 1, 1, 0.45))
        c.setFont("WorkSans", 8.5)
        c.drawString(exec_x + 35, yy2 - 24, line1)
        c.drawString(exec_x + 35, yy2 - 37, line2)
        c.restoreState()

        yy2 -= card_h + 8

    # Connecting visual between groups — dashed arc
    c.saveState()
    c.setStrokeColor(Color(1, 1, 1, 0.08))
    c.setLineWidth(0.6)
    c.setDash([3, 5])
    c.line(plan_x + card_w + 10, H / 2, exec_x - 10, H / 2)
    c.restoreState()

    # Arrow label
    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.2))
    c.setFont("DMMono", 5.5)
    c.drawCentredString((plan_x + card_w + exec_x) / 2, H / 2 + 6, "HANDOFF")
    c.restoreState()

    draw_page_number(c, 5, 8)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 6: BMAD VS TRADITIONAL AGILE
# ═════════════════════════════════════════════════════════════════════════════

def page_comparison(c):
    draw_base_background(c)
    draw_dot_grid(c, 50, 50, W - 100, H - 100, spacing=45, radius=0.3, color=Color(1, 1, 1, 0.015))
    draw_corner_marks(c, margin=35, size=18, color=Color(0.16, 0.75, 0.68, 0.3))
    draw_section_marker(c, "Section 05  —  Comparison")

    cx = W / 2

    # Title
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("BigShoulders-Bold", 44)
    c.drawCentredString(cx, H - 105, "BMAD vs Traditional Agile")
    c.restoreState()

    draw_horizontal_rule(c, H - 122, cx - 220, cx + 220, TEAL_LIGHT, 0.5)

    # ─── Two-column comparison ────────────────────────────────────────────
    col_w = 330
    col_h = 340
    gap = 40
    lx = cx - col_w - gap / 2
    rx = cx + gap / 2
    cy_card = 60

    # Left column: Traditional Agile
    draw_rounded_rect(c, lx, cy_card, col_w, col_h, r=4,
                      fill_color=Color(1, 1, 1, 0.025),
                      stroke_color=Color(1, 1, 1, 0.06), stroke_w=0.4)

    # Column header
    c.saveState()
    c.setFillColor(Color(0.83, 0.70, 0.50, 0.15))
    c.rect(lx, cy_card + col_h - 40, col_w, 40, fill=1, stroke=0)
    c.restoreState()

    c.saveState()
    c.setFillColor(AMBER_SOFT)
    c.setFont("InstrumentSans-Bold", 14)
    c.drawCentredString(lx + col_w / 2, cy_card + col_h - 27, "Traditional Agile")
    c.restoreState()

    trad_items = [
        "Human-only team members",
        "Source code as truth",
        "Informal handoffs via meetings",
        "Documentation is secondary",
        "Governance added separately",
        "Scales by hiring people",
        "Variable consistency",
    ]

    item_y = cy_card + col_h - 70
    for item in trad_items:
        # Bullet dot
        c.saveState()
        c.setFillColor(Color(0.83, 0.57, 0.04, 0.4))
        c.circle(lx + 25, item_y + 3, 2.5, fill=1, stroke=0)
        c.restoreState()
        # Text
        c.saveState()
        c.setFillColor(Color(1, 1, 1, 0.55))
        c.setFont("WorkSans", 10.5)
        c.drawString(lx + 38, item_y - 2, item)
        c.restoreState()
        item_y -= 36

    # Right column: BMAD Method
    draw_rounded_rect(c, rx, cy_card, col_w, col_h, r=4,
                      fill_color=Color(1, 1, 1, 0.025),
                      stroke_color=Color(0.16, 0.75, 0.68, 0.15), stroke_w=0.6)

    c.saveState()
    c.setFillColor(Color(0.10, 0.54, 0.49, 0.2))
    c.rect(rx, cy_card + col_h - 40, col_w, 40, fill=1, stroke=0)
    c.restoreState()

    c.saveState()
    c.setFillColor(TEAL_LIGHT)
    c.setFont("InstrumentSans-Bold", 14)
    c.drawCentredString(rx + col_w / 2, cy_card + col_h - 27, "BMAD Method")
    c.restoreState()

    bmad_items = [
        "AI agents as specialized team members",
        "Documentation as source of truth",
        "Structured artifact handoffs",
        "Documentation is first-class citizen",
        "Governance built into lifecycle",
        "Scales instantly with AI agents",
        "Consistent, predictable behavior",
    ]

    item_y = cy_card + col_h - 70
    for item in bmad_items:
        c.saveState()
        c.setFillColor(TEAL)
        c.circle(rx + 25, item_y + 3, 2.5, fill=1, stroke=0)
        c.restoreState()
        c.saveState()
        c.setFillColor(Color(1, 1, 1, 0.7))
        c.setFont("WorkSans", 10.5)
        c.drawString(rx + 38, item_y - 2, item)
        c.restoreState()
        item_y -= 36

    # Center "VS" divider
    c.saveState()
    c.setStrokeColor(Color(1, 1, 1, 0.08))
    c.setLineWidth(0.5)
    c.setDash([2, 4])
    c.line(cx, cy_card + 20, cx, cy_card + col_h - 50)
    c.restoreState()

    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.15))
    c.setFont("BigShoulders-Bold", 14)
    c.drawCentredString(cx, cy_card + col_h / 2 - 5, "VS")
    c.restoreState()

    draw_page_number(c, 6, 8)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 7: KEY BENEFITS
# ═════════════════════════════════════════════════════════════════════════════

def page_benefits(c):
    draw_base_background(c, SLATE_DARK, SLATE_MID)
    draw_grid_pattern(c, 0, 0, W, H, spacing=55, color=Color(1, 1, 1, 0.012))
    draw_corner_marks(c, margin=35, size=18, color=Color(0.16, 0.75, 0.68, 0.3))
    draw_section_marker(c, "Section 06  —  Value")

    # Title
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("BigShoulders-Bold", 48)
    c.drawString(80, H - 110, "Key Benefits")
    c.restoreState()

    draw_horizontal_rule(c, H - 128, 80, 320, TEAL_LIGHT, 0.5)

    # ─── Benefits as elegant grid ─────────────────────────────────────────
    benefits = [
        {
            "title": "Eliminates Planning",
            "title2": "Bottlenecks",
            "desc": "AI agents generate PRDs and architecture",
            "desc2": "docs with unprecedented precision.",
            "color": TEAL,
        },
        {
            "title": "Cost Optimization",
            "title2": "",
            "desc": "Front-loaded planning concentrates tokens",
            "desc2": "in high-value phases. Create once, reuse.",
            "color": TEAL_LIGHT,
        },
        {
            "title": "Built-in Governance",
            "title2": "& Compliance",
            "desc": "Every decision versioned and auditable.",
            "desc2": "SOC 2, HIPAA compliance simplified.",
            "color": INDIGO,
        },
        {
            "title": "Reduced",
            "title2": "Context Loss",
            "desc": "Structured handoffs with explicit artifacts",
            "desc2": "prevent context evaporation.",
            "color": AMBER,
        },
        {
            "title": "Security",
            "title2": "by Design",
            "desc": "Security requirements incorporated",
            "desc2": "from the planning phase, not bolted on.",
            "color": TEAL,
        },
        {
            "title": "Scales",
            "title2": "Instantly",
            "desc": "AI agents are always on and scale",
            "desc2": "without hiring or onboarding.",
            "color": TEAL_LIGHT,
        },
    ]

    cols = 3
    rows = 2
    card_w = 220
    card_h = 140
    h_gap = 28
    v_gap = 22
    total_w = cols * card_w + (cols - 1) * h_gap
    total_h = rows * card_h + (rows - 1) * v_gap
    sx = (W - total_w) / 2
    sy = (H - total_h) / 2 - 30

    for idx, benefit in enumerate(benefits):
        col = idx % cols
        row = idx // cols
        x = sx + col * (card_w + h_gap)
        y = sy + (rows - 1 - row) * (card_h + v_gap)

        draw_rounded_rect(c, x, y, card_w, card_h, r=3,
                          fill_color=Color(1, 1, 1, 0.03),
                          stroke_color=Color(1, 1, 1, 0.06), stroke_w=0.4)

        # Left accent bar
        c.saveState()
        c.setFillColor(benefit["color"])
        c.rect(x, y, 3, card_h, fill=1, stroke=0)
        c.restoreState()

        # Title
        c.saveState()
        c.setFillColor(IVORY)
        c.setFont("InstrumentSans-Bold", 13)
        c.drawString(x + 18, y + card_h - 30, benefit["title"])
        if benefit["title2"]:
            c.drawString(x + 18, y + card_h - 47, benefit["title2"])
        c.restoreState()

        # Separator
        sep_y = y + card_h - 58 if benefit["title2"] else y + card_h - 42
        c.saveState()
        c.setStrokeColor(Color(1, 1, 1, 0.08))
        c.setLineWidth(0.3)
        c.line(x + 18, sep_y, x + card_w - 18, sep_y)
        c.restoreState()

        # Description
        c.saveState()
        c.setFillColor(Color(1, 1, 1, 0.45))
        c.setFont("WorkSans", 8.5)
        c.drawString(x + 18, sep_y - 18, benefit["desc"])
        c.drawString(x + 18, sep_y - 32, benefit["desc2"])
        c.restoreState()

    draw_page_number(c, 7, 8)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 8: GETTING STARTED
# ═════════════════════════════════════════════════════════════════════════════

def page_getting_started(c):
    draw_base_background(c)

    cx, cy = W / 2, H / 2

    # Radial pattern — echoing cover but inverted energy
    c.saveState()
    c.setStrokeColor(Color(1, 1, 1, 0.025))
    c.setLineWidth(0.3)
    for angle in range(0, 360, 12):
        rad = math.radians(angle)
        x2 = cx + 500 * math.cos(rad)
        y2 = cy + 500 * math.sin(rad)
        c.line(cx, cy, x2, y2)
    c.restoreState()

    # Concentric circles
    c.saveState()
    for r in range(30, 250, 40):
        alpha = max(0.01, 0.05 - r * 0.0002)
        c.setStrokeColor(Color(0.16, 0.68, 0.62, alpha))
        c.setLineWidth(0.4)
        c.circle(cx, cy, r, fill=0, stroke=1)
    c.restoreState()

    draw_corner_marks(c, margin=35, size=18, color=Color(0.16, 0.75, 0.68, 0.3))
    draw_section_marker(c, "Section 07  —  Begin")

    # Central node
    draw_node_circle(c, cx, cy - 10, 4, fill_color=TEAL_LIGHT)

    # Title
    c.saveState()
    c.setFillColor(IVORY)
    c.setFont("BigShoulders-Bold", 52)
    c.drawCentredString(cx, H - 110, "Getting Started")
    c.restoreState()

    draw_horizontal_rule(c, H - 128, cx - 160, cx + 160, TEAL_LIGHT, 0.5)

    # ─── Resource blocks ──────────────────────────────────────────────────

    resources = [
        ("DOCUMENTATION", "docs.bmad-method.org", TEAL),
        ("GITHUB", "github.com/bmad-code-org/BMAD-METHOD", INDIGO),
        ("LICENSE", "MIT  //  100% Free & Open Source", AMBER),
    ]

    res_y = cy + 60
    for label, value, color in resources:
        # Label
        c.saveState()
        c.setFillColor(color)
        c.setFont("DMMono", 7)
        c.drawCentredString(cx, res_y, label)
        c.restoreState()

        # Value
        c.saveState()
        c.setFillColor(IVORY)
        c.setFont("Jura-Medium", 13)
        c.drawCentredString(cx, res_y - 20, value)
        c.restoreState()

        # Thin separator
        c.saveState()
        c.setStrokeColor(Color(1, 1, 1, 0.06))
        c.setLineWidth(0.3)
        c.line(cx - 140, res_y - 38, cx + 140, res_y - 38)
        c.restoreState()

        res_y -= 62

    # Closing statement
    c.saveState()
    c.setFillColor(TEAL_LIGHT)
    c.setFont("InstrumentSerif-Italic", 15)
    c.drawCentredString(cx, 115, "The future of development is")
    c.drawCentredString(cx, 95, "human + AI collaboration.")
    c.restoreState()

    # Bottom classification
    c.saveState()
    c.setFillColor(Color(1, 1, 1, 0.2))
    c.setFont("DMMono", 6.5)
    c.drawCentredString(cx, 50, "BMAD METHOD  //  SYSTEMATIC CONVERGENCE  //  2026")
    c.restoreState()

    draw_page_number(c, 8, 8)


# ═════════════════════════════════════════════════════════════════════════════
# BUILD PDF
# ═════════════════════════════════════════════════════════════════════════════

def build_pdf():
    pdf = canvas.Canvas(OUTPUT, pagesize=landscape(A4))
    pdf.setTitle("BMAD: A Beginner's Guide")
    pdf.setAuthor("Systematic Convergence")
    pdf.setSubject("Breakthrough Method for Agile AI-Driven Development")

    pages = [
        page_cover,
        page_what_is_bmad,
        page_core_principles,
        page_four_phases,
        page_agent_roles,
        page_comparison,
        page_benefits,
        page_getting_started,
    ]

    for i, page_fn in enumerate(pages):
        page_fn(pdf)
        if i < len(pages) - 1:
            pdf.showPage()

    pdf.save()
    print(f"PDF created: {OUTPUT}")
    print(f"Pages: {len(pages)}")
    print(f"Dimensions: {W:.0f} x {H:.0f} pt (landscape A4)")


if __name__ == "__main__":
    build_pdf()
