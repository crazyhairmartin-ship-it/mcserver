"""Paint the "dale" wolf coat (More Mob Variants) after Dylan's treeing walker coonhound, Dale.

    python tools/skins/make_dale.py

Dylan hand-edited the result into dale_hand_edited.png; when that file exists it's the source (see from_hand), so
rerunning this keeps his edits. Delete it to go back to the painted version.

Writes kubejs/assets/moremobvariants/textures/entity/wolf/dale_{wild,tame,angry}.png (64x32, vanilla wolf layout; the
pixel mask comes from vanilla_wolf_tame.png). The coat (kubejs/data/moremobvariants/variants/wolf/dale.json) spawns
nowhere (its biome tag fotf:nowhere is empty): it's given to a wolf by setting VariantID moremobvariants:dale. Dale: white with grey freckles on muzzle and legs, a tan face with a white
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

# each colour is a ramp of tones (dark -> light); the coat picks a tone per pixel from soft mottled noise plus a little
# speckle, the way More Mob Variants' own coats are painted, instead of flat fills
RAMPS = {
    'white': [(196, 190, 180), (214, 208, 198), (228, 223, 214), (238, 234, 226), (246, 243, 237)],
    'freckle': [(84, 78, 76), (104, 96, 92), (122, 114, 108)],
    'black': [(20, 19, 21), (30, 28, 30), (40, 37, 39), (52, 48, 50)],
    'tan': [(108, 60, 28), (128, 72, 34), (148, 86, 42), (166, 100, 50), (182, 116, 62)],
    'tan2': [(84, 46, 22), (100, 56, 27), (116, 66, 32)],
    'ear': [(66, 38, 20), (78, 46, 25), (92, 56, 30), (104, 64, 34)],
    'earfade': [(34, 24, 20), (44, 30, 22), (54, 36, 24)],
    'nose': [(18, 16, 18), (26, 24, 26)],
    'eye': [(34, 22, 14)],
}
WHITE, SHADE, FRECKLE, BLACK, BLACK2 = 'white', 'white', 'freckle', 'black', 'black'
TAN, TAN2, EAR, EAR2, NOSE, EYE = 'tan', 'tan2', 'ear', 'ear', 'nose', 'eye'
# faces whose lower rows are the underside / lower flank get shaded down: (x0, y0, x1, y1, shade per row from the top)
SHADING = [(18, 20, 24, 29, 0.0), (30, 20, 36, 29, 0.0), (24, 20, 30, 29, -0.35), (0, 20, 8, 28, -0.04),
           (10, 0, 16, 4, -0.3), (36, 0, 44, 7, -0.25)]


def mottle(x, y, seed):
    """Smooth-ish value noise in 0..1: blobs a few pixels across, so tones form patches rather than salt and pepper."""
    def h(i, j):
        return random.Random((i * 7349 + j * 1931 + seed * 104729) & 0xFFFFFFFF).random()
    total = 0.0
    for scale, weight in ((3.0, 0.6), (1.5, 0.4)):
        fx, fy = x / scale, y / scale
        i, j = int(fx), int(fy)
        tx, ty = fx - i, fy - j
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        top = h(i, j) * (1 - tx) + h(i + 1, j) * tx
        bottom = h(i, j + 1) * (1 - tx) + h(i + 1, j + 1) * tx
        total += weight * (top * (1 - ty) + bottom * ty)
    return total


def tone(cls, x, y, rnd):
    ramp = RAMPS[cls]
    v = mottle(x, y, 11) * 0.8 + rnd.random() * 0.35 - 0.05
    for x0, y0, x1, y1, per_row in SHADING:
        if x0 <= x < x1 and y0 <= y < y1:
            v += -0.06 * (y - y0) if per_row == 0.0 else per_row
    return ramp[max(0, min(len(ramp) - 1, int(v * len(ramp))))]


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
                px[(x, y)] = FRECKLE if r < freckles else WHITE

    def black(x0, y0, x1, y1):
        for y in range(y0, y1):
            for x in range(x0, x1):
                px[(x, y)] = BLACK

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
    fixed = {(4, 6): (255, 255, 255), (5, 6): (18, 20, 22), (8, 6): (18, 20, 22), (9, 6): (255, 255, 255),
             (5, 5): (255, 255, 255), (8, 5): (255, 255, 255)}     # white pixel above each eye, like vanilla
    if mood == 'angry':
        del fixed[(5, 5)], fixed[(8, 5)]
        for x in (4, 5, 8, 9):
            px[(x, 5)] = BLACK
        fixed = {(4, 6): (182, 15, 15), (5, 6): (228, 46, 46), (8, 6): (228, 46, 46), (9, 6): (182, 15, 15)}

    # muzzle: white with freckles, black nose at the front
    white(0, 10, 14, 17, 0.22)
    fill(4, 14, 7, 15, NOSE)
    px[(5, 15)] = NOSE

    # Dale's spots, from the photos: an oblong "Mickey" on his right side (two lobes toward the shoulder), a big
    # splotch on his left side that spills over the top of his back, and black over the top of his butt with a little
    # tan below it. Side faces run head -> tail down the rows; on the right side column 18 is the spine edge, on the left
    # side column 35 is. The shoulders (mane box) sit in front of the body, so the spots start on the mane's back rows
    # and carry on onto the body without a seam.
    def spot(cells):
        for x, y in cells:
            px[(x, y)] = BLACK

    def grid(x0, y0, rows, flip=False):
        """Cells from a picture: rows of '#'/'.' read top -> bottom = head -> tail, left -> right = spine -> belly
        (flip: right -> left, for the left side where the spine is on the right)."""
        out = []
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch == '#':
                    out.append((x0 - dx if flip else x0 + dx, y0 + dy))
        return out

    # shoulders (mane): white with ticking
    white(21, 0, 51, 13, 0.05)
    # right side of the mane (spine at x21): the Mickey's two lobes
    spot(grid(21, 10, ['.#.#..',
                       '.####.',
                       '.####.']))
    # left side of the mane (spine at x42): front of the splotch
    spot(grid(42, 10, ['##....',
                       '###...',
                       '####..'], flip=True))
    spot([(43, 11), (43, 12), (44, 12)])                    # splotch over the top, on the mane's back

    # body: white with ticking along the back
    white(18, 14, 42, 29, 0.05)
    white(36, 20, 42, 29, 0.10)
    # right side (spine at x18): the oblong Mickey, wide at the front, narrowing toward the hip
    spot(grid(18, 20, ['.####.',
                       '.#####',
                       '.#####',
                       '..####',
                       '..###.',
                       '...#..']))
    # left side (spine at x35): the big splotch, up over the spine
    spot(grid(35, 20, ['####..',
                       '#####.',
                       '#####.',
                       '####..',
                       '###...'], flip=True))
    spot([(36, 20), (37, 20), (36, 21), (37, 21), (36, 22), (36, 23)])   # spilling over the top of his back
    # top of the butt: black across the back's last rows and down onto both hips, a little tan under it
    black(36, 27, 42, 29)
    spot(grid(18, 27, ['###...', '###...']))
    spot(grid(35, 27, ['###...', '###...'], flip=True))
    for x, y in ((21, 27), (21, 28), (32, 27), (32, 28)):
        px[(x, y)] = TAN
    black(32, 17, 35, 20)                                   # rump, under the tail

    # legs: white, freckled toward the paws
    white(0, 18, 8, 23, 0.04)
    white(0, 23, 8, 28, 0.20)

    # tail: black at the base, white to the tip
    white(9, 18, 17, 28, 0.02)
    black(9, 20, 17, 22)
    black(11, 18, 15, 20)

    # ears last (their texture overlaps the body's unused corner): dark brown
    for y in range(14, 17):                                 # row 14 = top of the ear, 16 = where it meets the head
        for x in range(16, 22):
            px[(x, y)] = 'black' if y == 14 else 'earfade' if y == 15 else EAR

    for (x, y), c in px.items():
        if 0 <= x < 64 and 0 <= y < 32 and mask.getpixel((x, y))[3]:
            img.putpixel((x, y), fixed.get((x, y), tone(c, x, y, rnd)) + (255,))
    return img


HAND = HERE / 'dale_hand_edited.png'


def from_hand(mood):
    """Dylan's hand-edited Dale (dale_hand_edited.png, started from paint('tame')): used as-is for tame and wild; the
    angry one gets vanilla's angry eyes (dark brows, red eyes)."""
    img = Image.open(HAND).convert('RGBA')
    if mood == 'angry':
        for x in (4, 5, 8, 9):
            img.putpixel((x, 5), (30, 28, 30, 255))
        for p, c in {(4, 6): (182, 15, 15), (5, 6): (228, 46, 46), (8, 6): (228, 46, 46), (9, 6): (182, 15, 15)}.items():
            img.putpixel(p, c + (255,))
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for mood in ('wild', 'tame', 'angry'):
        # the hand-edited texture wins when it's there; paint() is how it started
        (from_hand(mood) if HAND.exists() else paint(mood)).save(OUT / f'dale_{mood}.png')
    print('wrote', ', '.join(f'dale_{m}.png' for m in ('wild', 'tame', 'angry')), '->', OUT)


if __name__ == '__main__':
    main()
