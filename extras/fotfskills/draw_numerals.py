"""Draws the 16x16 tier-label icons (I..V) and the OR icon used by the skill trees' marker tiles.

Writes res/assets/fotfskills/textures/gui/skills/tier_<n>.png and or.png. Run: python draw_numerals.py
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'res', 'assets', 'fotfskills', 'textures', 'gui', 'skills')
TEXT = (240, 226, 190, 255)        # warm parchment white
SHADE = (150, 124, 72, 255)        # lower half of each letter
OUTLINE = (40, 30, 20, 255)

# 7-row pixel glyphs ('#' = ink), variable width
GLYPHS = {
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'V': ['#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..', '..#..'],
    'O': ['.#.', '#.#', '#.#', '#.#', '#.#', '#.#', '.#.'],
    'R': ['##.', '#.#', '#.#', '##.', '#.#', '#.#', '#.#'],
}
LABELS = {'tier_1': 'I', 'tier_2': 'II', 'tier_3': 'III', 'tier_4': 'IV', 'tier_5': 'V', 'or': 'OR'}


def draw(text):
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    width = sum(len(GLYPHS[ch][0]) for ch in text) + (len(text) - 1)   # 1px gap between letters
    x0, y0 = (16 - width) // 2, (16 - 7) // 2
    ink = set()
    cursor = x0
    for ch in text:
        for y, row in enumerate(GLYPHS[ch]):
            for x, c in enumerate(row):
                if c == '#':
                    ink.add((cursor + x, y0 + y))
        cursor += len(GLYPHS[ch][0]) + 1
    for x, y in ink:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if p not in ink and 0 <= p[0] < 16 and 0 <= p[1] < 16:
                    img.putpixel(p, OUTLINE)
    for x, y in ink:
        img.putpixel((x, y), TEXT if y < y0 + 4 else SHADE)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, text in LABELS.items():
        draw(text).save(os.path.join(OUT, name + '.png'))
    preview = Image.new('RGBA', (6 * 100, 96), (60, 52, 44, 255))
    for i, name in enumerate(LABELS):
        big = Image.open(os.path.join(OUT, name + '.png')).resize((96, 96), Image.NEAREST)
        preview.paste(big, (i * 100, 0), big)
    preview.save(os.path.join(HERE, 'numerals_preview.png'))
    print('numerals drawn')


if __name__ == '__main__':
    main()
