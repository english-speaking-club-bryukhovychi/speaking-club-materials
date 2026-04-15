#!/usr/bin/env python3
"""
Generate cards.pdf from words/*.txt (or a supplied directory).
Layout : 2 columns × 10 rows = 20 cards per A4 page (portrait)
Card   : 105 mm × 29.7 mm  (fills A4 exactly; borders drawn inside)
Text   : uppercase, centred, ~8 mm (≈ 22.7 pt)
Usage  : python3 make_cards.py [words_dir]   (default: words/)
"""
import glob
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ── layout constants ────────────────────────────────────────────────────────
COLS, ROWS   = 2, 10
CARDS_PER_PG = COLS * ROWS
PAGE_W, PAGE_H = A4                    # 595.28 × 841.89 pt
CARD_W = PAGE_W / COLS
CARD_H = PAGE_H / ROWS
BORDER = 0.5                           # rule thickness in pt (~0.18 mm)
FONT_SIZE = 22.7                       # pt  ≈ 8 mm
FONT_NAME = "Helvetica-Bold"

# ── helpers ─────────────────────────────────────────────────────────────────
WORDS_DIR = sys.argv[1] if len(sys.argv) > 1 else "words"


def read_words(directory: str) -> list[str]:
    words: list[str] = []
    for path in sorted(glob.glob(os.path.join(directory, "*.txt"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                w = line.strip()
                if w:
                    words.append(w)
    return words


def draw_page(c: canvas.Canvas, page_words: list[str]) -> None:
    """Draw up to CARDS_PER_PG cards on the current canvas page."""
    for idx in range(CARDS_PER_PG):
        col = idx % COLS
        row = idx // COLS

        # PDF origin is bottom-left; we want top-left card first
        x = col * CARD_W
        y = PAGE_H - (row + 1) * CARD_H   # bottom of this cell

        # border rectangle
        c.setLineWidth(BORDER)
        c.rect(x, y, CARD_W, CARD_H)

        if idx >= len(page_words):
            continue

        text = page_words[idx].upper()

        # shrink font if text wider than 90 % of card
        font_size = FONT_SIZE
        max_w = CARD_W * 0.90
        while font_size > 6 and c.stringWidth(text, FONT_NAME, font_size) > max_w:
            font_size -= 0.5

        c.setFont(FONT_NAME, font_size)
        text_w = c.stringWidth(text, FONT_NAME, font_size)
        text_x = x + (CARD_W - text_w) / 2
        # vertically centre the text (baseline offset ≈ 0.35 × font_size)
        text_y = y + (CARD_H - font_size) / 2 + font_size * 0.15
        c.drawString(text_x, text_y, text)


# ── main ────────────────────────────────────────────────────────────────────
def main() -> None:
    words = read_words(WORDS_DIR)
    if not words:
        sys.exit(f"No words found in {WORDS_DIR}/*.txt")

    pages = [words[i : i + CARDS_PER_PG] for i in range(0, len(words), CARDS_PER_PG)]
    out = "cards.pdf"

    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle("Vocabulary Cards")

    for pi, page_words in enumerate(pages):
        draw_page(c, page_words)
        c.showPage()

    c.save()
    print(f"Saved {out}  ({len(words)} words, {len(pages)} page(s))")


if __name__ == "__main__":
    main()
