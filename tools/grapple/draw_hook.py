"""Draws new 16x16 textures for Grappling Hook - Reforged's basic hook (KubeJS asset overrides).

grapplinghook.png  the item and rope.png (shown while the hook is out) are Dylan's hand-drawn textures now: this script
                   never writes them (they used to be drawn here from the coil below)
entity/rope.png    the line stretched between you and the hook: a 2x16 braid in the same palette
entity_hook.png    the flying hook (also the "hook" item model): just the grapnel
Writes into kubejs/assets/grapplemod/textures/item/ plus an enlarged preview next to this script.
"""
import math
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'kubejs', 'assets', 'grapplemod', 'textures', 'item')

OUTLINE = (34, 30, 30, 255)
IRON = {'light': (206, 213, 220, 255), 'mid': (140, 148, 158, 255), 'dark': (84, 90, 100, 255), 'shine': (240, 244, 247, 255)}
ROPE = {'light': (173, 144, 94, 255), 'mid': (148, 113, 74, 255), 'dark': (110, 83, 60, 255)}   # jute (Supplementaries rope palette)


def line(a, b):
    """Pixels on a straight line from a to b (inclusive)."""
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0))
    return {(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)}


def grapnel(ox=0, oy=0):
    """Iron pixels of the grapnel head + shaft. Head centre at (11,4) before offset."""
    px = set()
    px |= line((6, 9), (12, 3))                                    # shaft
    px |= line((7, 9), (12, 4))                                    # shaft, second pixel wide
    px |= {(13, 2), (14, 1)}                                       # middle prong to a point
    px |= {(11, 2), (10, 1), (9, 1), (8, 2)}                       # upper prong curling back to a point
    px |= {(13, 4), (14, 5), (14, 6), (13, 7)}                     # lower prong curling back to a point
    return {(x + ox, y + oy) for x, y in px}


def eye(ox=0, oy=0):
    return {(x + ox, y + oy) for x, y in [(5, 10), (4, 10), (5, 11), (4, 11)]} - {(4, 11)}


def coil(cx, cy, r0=1.3, r1=2.7):
    px = set()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r0 <= d <= r1:
                px.add((x, y))
    return px


def paint(iron, rope, extra_rope_line=()):
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    filled = set(iron) | set(rope) | set(extra_rope_line)
    for (x, y) in rope | set(extra_rope_line):
        if 0 <= x < 16 and 0 <= y < 16:
            tone = 'light' if (x + y) % 3 == 0 else 'dark' if (x + y) % 3 == 2 else 'mid'
            img.putpixel((x, y), ROPE[tone])
    for (x, y) in iron:
        if not (0 <= x < 16 and 0 <= y < 16):
            continue
        up_left = (x - 1, y) not in filled or (x, y - 1) not in filled
        down_right = (x + 1, y) not in filled or (x, y + 1) not in filled
        tone = 'mid'
        if up_left and not down_right:
            tone = 'light'
        elif down_right and not up_left:
            tone = 'dark'
        img.putpixel((x, y), IRON[tone])
    # prong tips catch the light
    for tip in [(14, 1), (8, 2), (13, 7)]:
        if tip in iron:
            img.putpixel(tip, IRON['shine'])
    # outline: empty pixels touching filled ones (4-way)
    for y in range(16):
        for x in range(16):
            if (x, y) in filled:
                continue
            if any((x + dx, y + dy) in filled for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                img.putpixel((x, y), OUTLINE)
    return img


def wound_coil(cx, cy, r_in=1.3, r_out=5.0, gaps=(2.5, 3.8)):
    """A hank of rope wound in turns: light rope with darker lines between the turns."""
    rope, seams = set(), set()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r_in <= d <= r_out:
                (seams if any(abs(d - g) < 0.35 for g in gaps) else rope).add((x, y))
    return rope, seams


def paint_coil(img, rope, seams, cx=5.5, cy=10.5):
    """Lit from the top left: the near side of each turn is lighter, the far side darker; dark lines between turns."""
    for (x, y) in rope:
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        lit = -(dx + dy) / (math.hypot(dx, dy) * 1.414 + 1e-6)
        img.putpixel((x, y), (205, 178, 124, 255) if lit > 0.6 else ROPE['light'] if lit > 0.1 else ROPE['mid'])
    for (x, y) in seams:
        img.putpixel((x, y), ROPE['dark'])


def main():
    os.makedirs(OUT, exist_ok=True)
    rope, seams = wound_coil(5.5, 10.5)
    tail = line((8, 7), (10, 5))                                   # the rope's end runs up to the hook
    hook = grapnel(1, -1) | eye(5, -4)
    item = paint(hook - rope - seams, (set(tail) | rope | seams))
    paint_coil(item, rope, seams)
    held = paint(set(), set(tail) | set(line((10, 5), (14, 1))) | rope | seams)
    paint_coil(held, rope, seams)
    flying = paint(grapnel(-2, 2) | eye(-2, 2), set())

    # item and held are no longer saved: grapplinghook.png and rope.png are Dylan's hand-drawn versions
    braid = Image.new('RGBA', (2, 16))
    twist = [('light', 'dark'), ('mid', 'mid'), ('dark', 'light'), ('mid', 'mid')]   # strands crossing, like the pack's rope
    for y in range(16):
        left, right = twist[y % 4]
        braid.putpixel((0, y), ROPE[left])
        braid.putpixel((1, y), ROPE[right])
    entity_dir = os.path.join(OUT, '..', 'entity')
    os.makedirs(entity_dir, exist_ok=True)
    braid.save(os.path.join(entity_dir, 'rope.png'))
    flying.save(os.path.join(OUT, 'entity_hook.png'))
    print('hook textures written')


if __name__ == '__main__':
    main()
