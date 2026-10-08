"""Paint Dylan's cats as More Mob Variants cat coats: Mister (tuxedo) and Beast (dark grey).

    python tools/skins/make_cats.py

Starts from the vanilla tuxedo (black.png) and grey (british_shorthair.png) cat textures, which already have the
right markings in the right places, and repaints them through make_dale's mottled tone ramps. Writes
kubejs/assets/moremobvariants/textures/entity/cat/{mister,beast}.png. The coats spawn nowhere (biome tag
fotf:nowhere); naming a cat Mister or Beast/Beastmode gives it the coat (config/fotfskills-named-pets.json).

Cat layout notes: head 0,0 (top 5-10/0-5, chin 10-15/0-5, face 5-10/5-9), nose 0,24, right ear 0,10, left ear 6,10
(top 8/10-11, outer side 9-10/12), body 20,0 (chest 26-30/0-6, belly 26-30/6-22, back 36-40/6-22), tail 0,15 and 4,15,
back legs 8,13 (both legs share it; outer face of the left leg = 12-14/15-21), front legs 40,0.
"""
import colorsys
import random
from pathlib import Path
from PIL import Image
from make_dale import RAMPS, mottle

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'kubejs' / 'assets' / 'moremobvariants' / 'textures' / 'entity' / 'cat'

RAMPS = dict(RAMPS, slate=[(44, 45, 50), (54, 55, 61), (64, 65, 72), (75, 76, 83), (88, 89, 96)],
             pink=[(196, 128, 132), (214, 150, 152)])


def lum(c):
    return (c[0] * 299 + c[1] * 587 + c[2] * 114) / 1000


def repaint(src, classify, seed):
    """Each pixel -> (ramp, original brightness 0..1) or a fixed colour; ramps pick a tone from brightness + mottle."""
    rnd = random.Random(seed)
    img = Image.new('RGBA', src.size, (0, 0, 0, 0))
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = src.getpixel((x, y))
            if not a:
                continue
            got = classify(x, y, (r, g, b))
            if isinstance(got, tuple) and len(got) == 3 and isinstance(got[0], int):
                img.putpixel((x, y), got + (255,))
                continue
            ramp, bright = got
            tones = RAMPS[ramp]
            v = bright * 0.5 + mottle(x, y, seed) * 0.45 + rnd.random() * 0.2 - 0.05
            img.putpixel((x, y), tones[max(0, min(len(tones) - 1, int(v * len(tones))))] + (255,))
    return img


def mister():
    src = Image.open(HERE / 'vanilla_cat_black.png').convert('RGBA')
    white = {(7, 7), (7, 8), (3, 24), (3, 25)}                                 # stripe down the nose
    white |= {(x, y) for x in (12, 13) for y in range(17, 21)}                 # left back paw white further up

    def classify(x, y, c):
        h, s, v = colorsys.rgb_to_hsv(*(k / 255 for k in c))
        if (x, y) in white:
            return 'white', 0.8
        if s > 0.35 and 0.15 < h < 0.45:                                       # eyes: yellow-green
            return (196, 204, 72) if lum(c) > 60 else (24, 22, 26)
        if s > 0.25 and (h < 0.05 or h > 0.9):                                 # pink nose
            return 'pink', v
        if lum(c) > 150:
            return 'white', lum(c) / 255
        return 'black', lum(c) / 90

    img = repaint(src, classify, 21)
    for p in ((8, 10), (10, 12)):                                              # nick in the left ear
        img.putpixel(p, (0, 0, 0, 0))
    return img


def beast():
    src = Image.open(HERE / 'vanilla_cat_british_shorthair.png').convert('RGBA')
    tuft = {(27, 3), (28, 3), (27, 4), (28, 4), (28, 5), (27, 6), (28, 6)}     # white tuft on the chest

    def classify(x, y, c):
        h, s, v = colorsys.rgb_to_hsv(*(k / 255 for k in c))
        if (x, y) in tuft:
            return 'white', 0.7
        if s > 0.3 and 0.08 < h < 0.2:                                         # eyes: yellow-amber
            return (214, 170, 62)
        if lum(c) < 40:                                                        # pupils
            return (18, 17, 20)
        if s > 0.2 and (h < 0.05 or h > 0.9):
            return 'pink', v
        return 'slate', (lum(c) - 90) / 110

    return repaint(src, classify, 33)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mister().save(OUT / 'mister.png')
    beast().save(OUT / 'beast.png')
    print('wrote mister.png, beast.png ->', OUT)


if __name__ == '__main__':
    main()
