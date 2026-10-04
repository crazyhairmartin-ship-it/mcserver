"""Draws the 16x16 Pet Memento item texture (a gold locket with a pink heart).

Writes res/assets/fotfskills/textures/item/pet_memento.png. Run: python draw_memento.py
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'res', 'assets', 'fotfskills', 'textures', 'item', 'pet_memento.png')

OUTLINE = (58, 38, 20, 255)
GOLD = (232, 182, 64, 255)
GOLD_DARK = (176, 124, 36, 255)
GOLD_LIGHT = (255, 230, 140, 255)
PINK = (236, 92, 140, 255)
PINK_LIGHT = (255, 170, 200, 255)
CHAIN = (150, 150, 160, 255)

# rows of the locket ('o' outline, 'g' gold, 'd' dark gold, 'l' light gold, 'p' pink, 'w' pink highlight, 'c' chain)
ART = [
    '......cc........',
    '.....c..c.......',
    '......cc........',
    '.....oooo.......',
    '...oogggloo.....',
    '..ogglllggdo....',
    '..oglpwgpgdo....',
    '.ogglppppggdo...',
    '.oggpppppggdo...',
    '.oggppppppgdo...',
    '..ogpppppgdo....',
    '..oggpppgddo....',
    '...ogdpgddo.....',
    '....oddddo......',
    '.....oooo.......',
    '................',
]
COLORS = {'o': OUTLINE, 'g': GOLD, 'd': GOLD_DARK, 'l': GOLD_LIGHT, 'p': PINK, 'w': PINK_LIGHT, 'c': CHAIN}


def main():
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(ART):
        for x, ch in enumerate(row):
            if ch in COLORS:
                img.putpixel((x, y), COLORS[ch])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print('pet memento drawn')


if __name__ == '__main__':
    main()
