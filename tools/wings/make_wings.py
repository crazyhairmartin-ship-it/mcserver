"""Smaller, feathered wings for Wings Horns & Hooves (ultimate_unicorn_mod) pegasi and nightmares (KubeJS asset overrides).

    python tools/wings/make_wings.py [mod jar]     (default: the test server's copy)

Geometry: every horse shares magical_horse_model.geo.json. The four wing bones are scaled down around the shoulder pivot
(SCALE) and their cubes switch from box UV to per-face UV that point at the same texture squares, so the smaller wing
still shows the whole feather texture. Animations only rotate these bones, so flapping and folding are unchanged.
Griffins, hippogriffs and destriers use the same wing bones, so their wings shrink too.

Textures: the wing squares of the pegasus and nightmare skins are redrawn as feathers - small coverts along the leading
edge, long secondaries on the inner panel, and fanned primaries with gaps between their tips on the outer panel - in
each skin's own colours. Writes into kubejs/assets/ultimate_unicorn_mod/ plus a preview next to this script.
"""
import io
import json
import math
import os
import random
import sys
import zipfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PACK = HERE.parents[1]
OUT = PACK / 'kubejs' / 'assets' / 'ultimate_unicorn_mod'
JAR = PACK.parent / 'server-test' / 'data' / 'mods' / 'ultimate_unicorn_mod-1.20.1-2.0.0.jar'
GEO = 'assets/ultimate_unicorn_mod/geo/magical_horse_model.geo.json'
TEX = 'assets/ultimate_unicorn_mod/textures/entity/'
SCALE = 0.8                                     # the wing bones' size: the nightmare's wings fill it
WINGS = ('rightWing', 'rightWingTip', 'leftWing', 'leftWingTip')
ROOTS = {'rightWing': 'rightWing', 'rightWingTip': 'rightWing', 'leftWing': 'leftWing', 'leftWingTip': 'leftWing'}
INNER, TIP = (0, 122), (0, 164)                  # top-left of each panel's top-face square; the underside sits 42 px right
# skin -> feather length (1 fills the wing bones; pegasi draw shorter feathers so their wings look smaller) and colours:
# light (shaft), vane from mid to dark, rim (feather edge)
SKINS = {
    'pegasus_blue.png': (0.69, dict(light=(250, 252, 255), mid=(232, 236, 242), dark=(198, 206, 218), rim=(150, 160, 178))),
    'pegasus_big_blue.png': (0.69, dict(light=(242, 248, 255), mid=(206, 220, 236), dark=(166, 186, 210), rim=(112, 134, 166))),
    'nightmare_black.png': (1.0, dict(light=(96, 16, 16), mid=(30, 26, 28), dark=(14, 12, 13), rim=(6, 4, 5))),
    'nightmare_big_red.png': (1.0, dict(light=(150, 24, 20), mid=(70, 12, 12), dark=(30, 8, 8), rim=(8, 4, 4))),
    'kirin_golden.png': (1.0, dict(light=(252, 226, 128), mid=(222, 180, 62), dark=(170, 126, 38), rim=(112, 78, 22))),
}
# every other skin a winged hybrid can wear: full-size feathers in colours taken from that skin's old wing art
OTHER_SKINS = ('deer.png', 'destrier_brown.png', 'destrier_red_wing_blackbird.png', 'griffin.png', 'hippocamp.png',
               'hippocamp_celestial_sea_horse.png', 'hippogriff.png', 'kevin.png', 'kirin.png', 'kirin_golden.png',
               'magical_horse.png', 'oracle.png', 'unicorn_rainbow_smash.png', 'unicorn_white.png')


def auto_colours(base):
    return dict(light=shade(base, 1.22), mid=base, dark=shade(base, 0.78), rim=shade(base, 0.52))


# ---------- geometry ----------

def box_faces(uv, size):
    """GeckoLib's box-UV layout (BakedModelFactory.buildQuad) as per-face UVs."""
    u, v = uv
    w, h, d = (math.floor(s) for s in size)
    faces = {'west': ([u + d + w, v + d], [d, h]), 'east': ([u, v + d], [d, h]),
             'north': ([u + d, v + d], [w, h]), 'south': ([u + d + w + d, v + d], [w, h]),
             'up': ([u + d, v], [w, d]), 'down': ([u + d + w, v + d], [w, -d])}
    return {k: {'uv': a, 'uv_size': b} for k, (a, b) in faces.items() if b[0] != 0 and b[1] != 0}


def shrink(geo):
    bones = {b['name']: b for b in geo['minecraft:geometry'][0]['bones']}
    pivots = {name: bones[name]['pivot'] for name in ('rightWing', 'leftWing')}

    def scaled(point, root):
        p = pivots[root]
        return [round(p[i] + (point[i] - p[i]) * SCALE, 4) for i in range(3)]

    for name in WINGS:
        bone, root = bones[name], ROOTS[name]
        if name != root:
            bone['pivot'] = scaled(bone['pivot'], root)
        for cube in bone['cubes']:
            uv = list(cube['uv'])
            if name.startswith('left'):
                uv[1] += 1                      # the left wing read its squares one row too high
            cube['uv'] = box_faces(uv, cube['size'])
            if cube['size'][1] < 0.5:
                # Feather planes. GeckoLib puts a face's texture top at the wing's back edge, and a "mirror" cube also
                # swaps its top and bottom faces (front-to-back reversed, underside shading on top). So: no mirror flag;
                # flip every plane front-to-back, and give the left wing a hand-mirrored (left-right flipped) mapping.
                cube.pop('mirror', None)
                for face in ('up', 'down'):
                    f = cube['uv'][face]
                    f['uv'] = [f['uv'][0], f['uv'][1] + f['uv_size'][1]]
                    f['uv_size'] = [f['uv_size'][0], -f['uv_size'][1]]
                    if name.startswith('left'):
                        f['uv'] = [f['uv'][0] + f['uv_size'][0], f['uv'][1]]
                        f['uv_size'] = [-f['uv_size'][0], f['uv_size'][1]]
            cube['origin'] = scaled(cube['origin'], root)
            cube['size'] = [round(s * SCALE, 4) if s > 0.5 else s for s in cube['size']]
    return geo


# ---------- feathers ----------

def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, k):
    """Lighter (k > 1) or darker (k < 1) without changing the hue's strength: pale feathers stay pale."""
    return tuple(max(0, min(255, round(x * k))) for x in c)


def base_colour(img):
    """Average colour of the old wing's top faces."""
    px = [img.getpixel((x, y)) for (x0, y0) in (INNER, TIP) for x in range(x0, x0 + 42) for y in range(y0, y0 + 42)]
    px = [p for p in px if p[3] > 0]
    return tuple(sum(p[i] for p in px) // len(px) for i in range(3))


class Panel:
    """A 42x42 RGBA canvas; later feathers paint over earlier ones (so draw back to front)."""

    def __init__(self):
        self.px = {}

    def put(self, x, y, c):
        if 0 <= x < 42 and 0 <= y < 42:
            self.px[(x, y)] = c

    def feather(self, base, angle, length, width, colours, rnd):
        """A feather from base along angle (radians, 0 = +x, pi/2 = +y): rounded tip, dark rim, light shaft."""
        light, mid, dark, rim = colours
        dx, dy = math.cos(angle), math.sin(angle)
        nx, ny = -dy, dx
        def half_at(t):
            return max(0.6, width / 2 * (1 - (t - 0.82) / 0.18 * 0.85 if t > 0.82 else 1))  # taper into a rounded tip

        cells = {}
        steps = int(length * 3)
        for i in range(steps + 1):
            t = i / steps
            half = half_at(t)
            for j in range(-int(half * 3), int(half * 3) + 1):
                s = j / 3
                cells[(int(math.floor(base[0] + dx * length * t + nx * s)),
                       int(math.floor(base[1] + dy * length * t + ny * s)))] = 0
        for (x, y) in cells:                                     # how far each pixel's centre sits from the shaft
            rx, ry = x + 0.5 - base[0], y + 0.5 - base[1]
            t = max(0.0, min(1.0, (rx * dx + ry * dy) / length))
            cells[(x, y)] = abs(rx * nx + ry * ny) / half_at(t)
        for (x, y), edge in cells.items():
            if edge > 0.78:
                c = rim
            elif edge < 0.13:
                c = light                                        # the shaft
            else:
                c = lerp(mid, dark, (edge - 0.18) / 0.6)
            noise = rnd.uniform(0.94, 1.06)
            self.put(x, y, shade(c, noise) if c != rim else c)

    def image(self, dim=1.0):
        im = Image.new('RGBA', (42, 42))
        for (x, y), c in self.px.items():
            im.putpixel((x, y), shade(c, dim) + (255,))
        return im


def palette(colours, k=1.0):
    return tuple(shade(colours[n], k) for n in ('light', 'mid', 'dark', 'rim'))


def draw_inner(colours, k, rnd):
    """Inner panel: leading edge on top, tip side on the left, body on the right. Secondaries hang to the trailing edge."""
    p = Panel()
    sec = palette(colours, 0.92)
    for i, x in enumerate(range(1, 42, 5)):                       # secondaries, back to front from the body side
        length = (38 - (2 if i % 2 else 0) - max(0, x - 34)) * k  # shorter near the body, alternating tips
        p.feather((x + 2.5, 2), math.pi / 2 + 0.05, length, 6.5, sec, rnd)
    for row, (y, w, ln) in enumerate(((14, 6, 9), (8, 5, 8), (2, 4, 7))):   # three rows of coverts over the shafts
        for x in range(-2 + row * 2, 44, w - 1):
            if x > 39 - (row == 2) * 3 and y < 6:
                continue                                         # keep the rounded shoulder corner
            p.feather((x + w / 2, (y - 2) * k), math.pi / 2, ln * k, w, palette(colours, 1.0 + row * 0.06), rnd)
    for x in range(0, 42):                                       # leading edge: a light line of marginal feathers
        for y in range(0, 2):
            if (x, y) in p.px and not (x > 37 and y < 2):
                p.put(x, y, colours['light'])
    return p


def draw_tip(colours, k, rnd):
    """Outer panel: wrist at top right, primaries fanning out to the left (outward) and down (back)."""
    p = Panel()
    pri = palette(colours, 0.85)
    feathers = 7
    scale = k
    for i in range(feathers):                                     # innermost first so the outer ones lie on top
        t = i / (feathers - 1)
        angle = math.pi / 2 + math.radians(6 + 72 * t)           # from straight back (down) to almost along the edge (left)
        p.feather((40 - i * 0.8, 3 + i * 0.6), angle, (32 + 9 * t) * scale, 6, pri, rnd)
    for row, (y, w, ln) in enumerate(((9, 6, 10), (3, 5, 8))):   # coverts over the primary bases near the wrist
        for x in range(22 + row * 4, 44, w - 1):
            p.feather((x + w / 2, (y - 3) * k), math.pi / 2 + 0.25, ln * k, w, palette(colours, 1.0 + row * 0.06), rnd)
    return p


def redraw(img, colours, k):
    rnd = random.Random(7)
    for (x0, y0), panel in ((INNER, draw_inner(colours, k, rnd)), (TIP, draw_tip(colours, k, rnd))):
        top, under = panel.image(), panel.image(0.82)
        for dx in range(84):                                     # clear both faces of the square first
            for dy in range(42):
                img.putpixel((x0 + dx, y0 + dy), (0, 0, 0, 0))
        img.paste(top, (x0, y0))
        img.paste(under, (x0 + 42, y0))                          # the underside: same feathers, a bit darker
    return img


def main():
    jar = zipfile.ZipFile(sys.argv[1] if len(sys.argv) > 1 else JAR)
    geo = shrink(json.loads(jar.read(GEO)))
    (OUT / 'geo').mkdir(parents=True, exist_ok=True)
    (OUT / 'geo' / 'magical_horse_model.geo.json').write_text(json.dumps(geo, indent=2) + '\n', encoding='utf-8')
    (OUT / 'textures' / 'entity').mkdir(parents=True, exist_ok=True)
    previews = []
    for skin in list(SKINS) + [s for s in OTHER_SKINS if s not in SKINS]:
        img = Image.open(io.BytesIO(jar.read(TEX + skin))).convert('RGBA')
        k, colours = SKINS.get(skin) or (1.0, auto_colours(base_colour(img)))
        redraw(img, colours, k).save(OUT / 'textures' / 'entity' / skin)
        previews.append(img.crop((0, 120, 86, 208)))
    cols = 6
    sheet = Image.new('RGBA', (cols * 90 * 2, ((len(previews) + cols - 1) // cols) * 90 * 2), (70, 70, 70, 255))
    for i, im in enumerate(previews):
        big = im.resize((86 * 2, 88 * 2), Image.NEAREST)
        sheet.paste(big, ((i % cols) * 180, (i // cols) * 180), big)
    sheet.save(HERE / 'preview.png')
    print(f'wings: geometry x{SCALE}, {len(previews)} skins redrawn')


if __name__ == '__main__':
    main()
