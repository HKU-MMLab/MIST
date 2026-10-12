"""Draw the README logo, loop, and findings cards.

The figures are schematics of the reported protocol. They are not plots
recomputed from the deleted experiment tree.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ROMAN = "/usr/share/texmf/fonts/opentype/public/lm/lmroman12-bold.otf"

TEAL = (15, 110, 86)
TEAL_SOFT = (232, 243, 239)
GOLD = (176, 141, 87)
INK = (28, 36, 48)
MUTED = (96, 104, 112)
PAPER = (247, 244, 238)
WHITE = (255, 255, 255)
LINE = (214, 206, 194)
BROWN = (139, 94, 75)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, xy, text, face, fill):
    draw.text(xy, text, font=face, fill=fill, anchor="mm")


def draw_lid(draw, x, y, w, h, opened: bool):
    body_top = y + h * 0.42
    rounded(draw, (x, body_top, x + w, y + h), 5, (232, 243, 239))
    if opened:
        lid = [
            (x + w * 0.08, body_top + 2),
            (x + w * 0.22, y + 2),
            (x + w * 0.96, y + h * 0.08),
            (x + w * 0.82, body_top - 2),
        ]
        draw.polygon(lid, fill=GOLD)
    else:
        draw.rectangle((x + 2, y + h * 0.22, x + w - 2, body_top + 2), fill=TEAL)


def draw_mark(draw, x, y, size):
    rounded(draw, (x, y, x + size, y + size), int(size * 0.18), TEAL)
    pad = int(size * 0.16)
    gap = int(size * 0.045)
    fw = (size - 2 * pad - 2 * gap) // 3
    fh = int(size * 0.62)
    top = y + (size - fh) // 2
    for i in range(3):
        fx = x + pad + i * (fw + gap)
        rounded(draw, (fx, top, fx + fw, top + fh), max(6, size // 18), (255, 255, 255, 255))
        inset = fw * 0.18
        draw_lid(
            draw,
            fx + inset,
            top + fh * 0.22,
            fw - 2 * inset,
            fh * 0.52,
            opened=(i == 2),
        )


def logo():
    w, h = 860, 360
    image = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(image)
    rounded(draw, (8, 8, w - 8, h - 8), 28, PAPER, LINE, 3)
    draw_mark(draw, 48, 48, 264)
    draw.text((352, 58), "MIST", font=font(ROMAN, 92), fill=INK)
    draw.text((356, 188), "Execution before memory", font=font(SANS, 30), fill=MUTED)
    draw.text((356, 242), "Make the Missing Move", font=font(SANS, 24), fill=TEAL)
    image.save(HERE / "logo.png", "PNG")


def shot_card(draw, box, index, title, body, accent):
    x0, y0, x1, y1 = box
    rounded(draw, box, 22, WHITE, LINE, 3)
    draw.rectangle((x0, y0 + 18, x0 + 10, y1 - 18), fill=accent)
    circle = (x0 + 36, y0 + 28, x0 + 92, y0 + 84)
    rounded(draw, circle, 28, TEAL_SOFT)
    center_text(draw, ((circle[0] + circle[2]) / 2, (circle[1] + circle[3]) / 2), str(index), font(SANS_BOLD, 28), TEAL)
    draw.text((x0 + 112, y0 + 36), title, font=font(SANS_BOLD, 32), fill=INK)
    draw.multiline_text((x0 + 40, y0 + 118), body, font=font(SANS, 24), fill=MUTED, spacing=8)


def arrow(draw, x, y):
    draw.polygon([(x, y - 10), (x + 22, y), (x, y + 10)], fill=GOLD)


def loop():
    w, h = 2000, 760
    image = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(image)
    rounded(draw, (8, 8, w - 8, h - 8), 28, PAPER, LINE, 3)
    draw.text((48, 36), "MIST", font=font(SANS_BOLD, 28), fill=TEAL)
    draw.text((140, 40), "three 5-second shots, target hidden until the last shot", font=font(SANS, 24), fill=MUTED)
    cards = [
        (1, "Setup", "The scene is set.\nThe change stays hidden."),
        (2, "Gap", "The lid stays closed.\nLeak before reveal: 0/43."),
        (3, "Reveal", "The model is asked to\nshow the change."),
    ]
    gap = 36
    card_w = 560
    left = 48
    top = 100
    for i, (index, title, body) in enumerate(cards):
        x = left + i * (card_w + gap)
        shot_card(draw, (x, top, x + card_w, top + 250), index, title, body, TEAL if i < 2 else GOLD)
        if i < 2:
            arrow(draw, x + card_w + 7, top + 125)

    draw.text((48, 400), "M3-Agent", font=font(SANS_BOLD, 28), fill=TEAL)
    draw.text((230, 404), "read the last frame, rewrite only the failed move, keep the best score", font=font(SANS, 24), fill=MUTED)
    steps = [
        ("1", "Read", "Last frame only"),
        ("2", "Diagnose", "Visible failure"),
        ("3", "Rewrite", "The failed move"),
        ("4", "Keep", "Oracle score"),
    ]
    step_w = 430
    step_gap = 28
    y = 460
    for i, (num, title, body) in enumerate(steps):
        x = 48 + i * (step_w + step_gap)
        rounded(draw, (x, y, x + step_w, y + 150), 18, WHITE, LINE, 3)
        center_text(draw, (x + 42, y + 75), num, font(SANS_BOLD, 28), TEAL)
        draw.text((x + 78, y + 36), title, font=font(SANS_BOLD, 30), fill=INK)
        draw.text((x + 78, y + 84), body, font=font(SANS, 24), fill=MUTED)
        if i < 3:
            arrow(draw, x + step_w + 3, y + 75)
    draw.text(
        (48, 680),
        "The original clip stays eligible. A worse rewrite is not kept. Keep-best sees the judge.",
        font=font(SANS, 22),
        fill=BROWN,
    )
    image.save(HERE / "loop.png", "PNG")


def finding_card(draw, box, kicker, number, lines):
    x0, y0, x1, y1 = box
    rounded(draw, box, 22, WHITE, LINE, 3)
    draw.rectangle((x0, y0 + 22, x0 + 10, y1 - 22), fill=TEAL)
    draw.text((x0 + 36, y0 + 28), kicker, font=font(SANS_BOLD, 22), fill=TEAL)
    draw.text((x0 + 36, y0 + 70), number, font=font(ROMAN, 54), fill=INK)
    draw.multiline_text((x0 + 36, y0 + 160), lines, font=font(SANS, 24), fill=MUTED, spacing=10)


def findings():
    w, h = 2000, 460
    image = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(image)
    cards = [
        ("FINDING 1  ·  INTERNAL", "41 / 43", "never open on the baseline\nsetup 0.852    leak 0/43\nreveal  0.147  →  0.492"),
        ("FINDING 2  ·  BEST OF FIVE", "0.763", "oracle, answer in the prompt\nanswer only  0.684\ntarget withheld  0.174"),
        ("FINDING 3  ·  OFFICIAL", "23 / 30", "baseline clips kept on MBench-T\nWRBench T   0.452 → 0.570\nMBench-T U   0.292 → 0.446"),
    ]
    gap = 28
    card_w = (w - 64 - 2 * gap) // 3
    for i, (kicker, number, lines) in enumerate(cards):
        x = 32 + i * (card_w + gap)
        finding_card(draw, (x, 24, x + card_w, h - 24), kicker, number, lines)
    image.save(HERE / "findings.png", "PNG")


if __name__ == "__main__":
    logo()
    loop()
    findings()
    print("wrote", HERE)
