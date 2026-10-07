"""Paint the "dale" wolf coat (More Mob Variants) after Dylan's treeing walker coonhound, Dale.

    python tools/skins/make_dale.py

Writes kubejs/assets/moremobvariants/textures/entity/wolf/dale_{wild,tame,angry}.png (64x32, vanilla wolf layout; the
pixel mask comes from vanilla_wolf_tame.png). The coat is name-tag only (kubejs/data/moremobvariants/variants/wolf/
dale.json): any wolf named "Dale" wears it. Dale: white with grey freckles on muzzle and legs, a tan face with a white
blaze, dark brown ears, a big black heart-shaped saddle over the back and sides, black at the tail base.

Wolf layout notes (body and mane boxes are rotated so their texture rows run head -> tail):
  head 0,0 (top 4-10/0-4, face 4-10/4-10, sides 0-4 and 10-14, back 14-20), muzzle 0,10, ears 16,14,
  mane 21,0, body 18,14 (chest 24-30/14-20, rump 30-36/14-20, right side 18-24, belly 24-30, left 30-36, back 36-42
  over rows 20-29), legs 0,18, tail 9,18 (rows 20-21 = base).
"""
import random
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'kubejs' / 'assets' / 'moremobvariants' / 'textures' / 'entity' / 'wolf'

WHITE = (236, 232, 224)
SHADE = (214, 208, 198)
FRECKLE = (104, 96, 92)
BLACK = (30, 28, 30)
BLACK2 = (46, 42, 44)
TAN = (156, 92, 44)
TAN2 = (118, 66, 32)
EAR = (82, 48, 26)
EAR2 = (98, 60, 32)
NOSE = (22, 20, 22)
EYE = (34, 22, 14)


def paint(mood):
    mask = Image.open(HERE / 'vanilla_wolf_tame.png').convert('RGBA')
    rnd = random.Random(7)
    img = Image.new('RGBA', mask.size, (0, 0, 0, 0))
    px = {}

    def fill(x0, y0, x1, y1, color):
        for y in range(y0, y1):
            for x in range(x0, x1):
                px[(x, y)] = color

    def white(x0, y0, x1, y1, freckles=0.0):
        for y in range(y0, y1):
            for x in range(x0, x1):
                r = rnd.random()
                px[(x, y)] = FRECKLE if r < freckles else SHADE if r < freckles + 0.18 else WHITE

    def black(x0, y0, x1, y1):
        for y in range(y0, y1):
            for x in range(x0, x1):
                px[(x, y)] = BLACK2 if rnd.random() < 0.25 else BLACK

    # everything starts white, lightly ticked
    white(0, 0, 64, 32, 0.03)

    # head: tan with a white blaze down the middle
    for x in range(4, 10):                                  # top of head
        for y in range(0, 4):
            px[(x, y)] = WHITE if x in (6, 7) else TAN2 if y == 0 else TAN
    fill(10, 0, 16, 4, WHITE)                               # under the jaw
    for y in range(4, 10):                                  # sides of the head
        for x in list(range(0, 4)) + list(range(10, 14)):
            px[(x, y)] = WHITE if y == 9 else TAN2 if x in (0, 13) else TAN
    for y in range(4, 10):                                  # back of the head: dark brown into black at the neck
        for x in range(14, 20):
            px[(x, y)] = BLACK if y >= 8 else TAN2
    face = [
        [TAN, TAN, WHITE, WHITE, TAN, TAN],
        [TAN, TAN, WHITE, WHITE, TAN, TAN],
        [TAN2, EYE, WHITE, WHITE, EYE, TAN2],
        [TAN, TAN, WHITE, WHITE, TAN, TAN],
        [TAN, TAN, WHITE, WHITE, TAN, TAN],
        [TAN, WHITE, WHITE, WHITE, WHITE, TAN],
    ]
    for dy, row in enumerate(face):
        for dx, c in enumerate(row):
            px[(4 + dx, 4 + dy)] = c
    if mood == 'angry':
        for x in (4, 5, 8, 9):
            px[(x, 5)] = BLACK
        px[(4, 6)], px[(5, 6)], px[(8, 6)], px[(9, 6)] = (182, 15, 15), (228, 46, 46), (228, 46, 46), (182, 15, 15)

    # muzzle: white with freckles, black nose at the front
    white(0, 10, 14, 17, 0.22)
    fill(4, 14, 7, 15, NOSE)
    px[(5, 15)] = NOSE

    # mane (neck and shoulders): white; the saddle starts at its back edge
    white(21, 0, 51, 13, 0.04)
    black(45, 12, 50, 13)

    # body: white chest and belly, black heart-shaped saddle over the back and down both sides
    white(18, 14, 42, 29, 0.04)
    black(36, 21, 42, 27)                                   # back
    for x, y in ((36, 21), (41, 21), (38, 26), (39, 26)):   # heart: two lobes at the shoulders, point at the rump
        px[(x, y)] = WHITE
    black(36, 26, 38, 27)
    black(40, 26, 42, 27)
    black(38, 28, 40, 29)                                   # black over the tail base
    black(18, 21, 21, 27)                                   # right side, from the back edge
    black(21, 22, 22, 26)
    black(33, 21, 36, 27)                                   # left side, from the back edge
    black(32, 22, 33, 26)
    black(32, 17, 35, 20)                                   # rump, under the tail

    # legs: white, freckled toward the paws
    white(0, 18, 8, 23, 0.04)
    white(0, 23, 8, 28, 0.20)

    # tail: black at the base, white to the tip
    white(9, 18, 17, 28, 0.02)
    black(9, 20, 17, 22)
    black(11, 18, 15, 20)

    # ears last (their texture overlaps the body's unused corner): dark brown
    for y in range(14, 17):
        for x in range(16, 22):
            px[(x, y)] = EAR2 if (x + y) % 3 == 0 else EAR

    for (x, y), c in px.items():
        if 0 <= x < 64 and 0 <= y < 32 and mask.getpixel((x, y))[3]:
            img.putpixel((x, y), c + (255,))
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for mood in ('wild', 'tame', 'angry'):
        paint(mood).save(OUT / f'dale_{mood}.png')
    print('wrote', ', '.join(f'dale_{m}.png' for m in ('wild', 'tame', 'angry')), '->', OUT)


if __name__ == '__main__':
    main()
