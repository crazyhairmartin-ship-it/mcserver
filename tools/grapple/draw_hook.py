"""Draws new 16x16 textures for Grappling Hook - Reforged's basic hook (KubeJS asset overrides).

grapplinghook.png  the item: iron grapnel (three prongs) top-right, shaft, rope coil bottom-left
rope.png           shown while the hook is out: the coil with the line running off toward the hook
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
ROPE = {'light': (179, 123, 67, 255), 'mid': (123, 79, 30, 255), 'dark': (81, 45, 19, 255)}   # Farmer's Delight rope palette


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


def main():
    os.makedirs(OUT, exist_ok=True)
    rope_coil = coil(3.5, 12.5)
    tie = {(4, 11), (3, 10)}                                       # rope tied through the eye

    item = paint(grapnel() | eye(), rope_coil | tie)
    held = paint(set(), rope_coil, extra_rope_line=line((4, 10), (14, 1)) - rope_coil)
    flying = paint(grapnel(-2, 2) | eye(-2, 2), set())

    item.save(os.path.join(OUT, 'grapplinghook.png'))
    held.save(os.path.join(OUT, 'rope.png'))
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

    preview = Image.new('RGBA', (3 * 192 + 40, 192), (58, 64, 60, 255))
    for i, im in enumerate((item, held, flying)):
        big = im.resize((192, 192), Image.NEAREST)
        preview.paste(big, (i * 212, 0), big)
    preview.save(os.path.join(HERE, 'preview.png'))
    print('hook textures written')


if __name__ == '__main__':
    main()
