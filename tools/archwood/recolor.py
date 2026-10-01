"""Recolor Ars Nouveau archwood textures so the planks average to TARGET, keeping grain/shading.

Works in CIELAB: each wood pixel keeps its offset from the original plank average, and the average
moves to TARGET. Only pixels close to the plank palette are changed, so metal and outlines stay.
Writes recolored textures to out/ and a before/after preview.png.
"""
import glob
import math
import os
import sys

from PIL import Image

TARGET = sys.argv[1] if len(sys.argv) > 1 else '#8d98cc'
MATCH_DE = float(sys.argv[2]) if len(sys.argv) > 2 else 14.0
ROOT = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(ROOT, 'orig')
OUT = os.path.join(ROOT, 'out')


def srgb_to_lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_to_srgb(c):
    c = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return max(0, min(255, round(c * 255)))


def rgb_to_lab(r, g, b):
    r, g, b = srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def lab_to_rgb(L, a, b):
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200
    inv = lambda t: t ** 3 if t ** 3 > 0.008856 else (t - 16 / 116) / 7.787
    x, y, z = inv(fx) * 0.95047, inv(fy), inv(fz) * 1.08883
    r = 3.2406 * x - 1.5372 * y - 0.4986 * z
    g = -0.9689 * x + 1.8758 * y + 0.0415 * z
    bl = 0.0557 * x - 0.2040 * y + 1.0570 * z
    return lin_to_srgb(r), lin_to_srgb(g), lin_to_srgb(bl)


planks = Image.open(glob.glob(os.path.join(ORIG, '**', 'archwood_planks.png'), recursive=True)[0]).convert('RGBA')
plank_px = [p[:3] for p in planks.getdata() if p[3] > 0]
palette = {rgb_to_lab(*p) for p in set(plank_px)}
labs = [rgb_to_lab(*p) for p in plank_px]
mean = [sum(c[i] for c in labs) / len(labs) for i in range(3)]
t = TARGET.lstrip('#')
target = rgb_to_lab(int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16))
mean_rgb = lab_to_rgb(*mean)
print(f'original plank average #{mean_rgb[0]:02x}{mean_rgb[1]:02x}{mean_rgb[2]:02x} -> target {TARGET}')


def is_wood(lab):
    return any(math.dist(lab, p) < MATCH_DE for p in palette)


def recolor(img):
    img = img.convert('RGBA')
    px = img.load()
    changed = 0
    for yy in range(img.height):
        for xx in range(img.width):
            r, g, b, a = px[xx, yy]
            if a == 0:
                continue
            lab = rgb_to_lab(r, g, b)
            if not is_wood(lab):
                continue
            new = tuple(lab[i] - mean[i] + target[i] for i in range(3))
            px[xx, yy] = (*lab_to_rgb(*new), a)
            changed += 1
    return img, changed


results = {}
for path in sorted(glob.glob(os.path.join(ORIG, '**', '*.png'), recursive=True)):
    rel = os.path.relpath(path, ORIG)
    img, changed = recolor(Image.open(path))
    dest = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    img.save(dest)
    results[rel.replace('\\', '/')] = (Image.open(path).convert('RGBA'), img)
    print(f'{changed:5d} px  {rel}')


def find(name):
    return next(v for k, v in results.items() if k.endswith(name))


# Preview: before (top row) / after (bottom row) of planks (3x3), door, trapdoor and chest, upscaled.
def tile3(img):
    t = Image.new('RGBA', (img.width * 3, img.height * 3))
    for i in range(3):
        for j in range(3):
            t.paste(img, (i * img.width, j * img.height))
    return t


def door(pair_top, pair_bottom, idx):
    top, bottom = pair_top[idx], pair_bottom[idx]
    d = Image.new('RGBA', (top.width, top.height * 2))
    d.paste(top, (0, 0))
    d.paste(bottom, (0, top.height))
    return d


S = 8
rows = []
for idx in (0, 1):
    parts = [tile3(find('block/archwood_planks.png')[idx]),
             door(find('archwood_door_top.png'), find('archwood_door_bottom.png'), idx),
             find('block/archwood_trapdoor.png')[idx],
             find('model/chest/archwood/archwood.png')[idx]]
    parts = [p.resize((p.width * S, p.height * S), Image.NEAREST) for p in parts]
    h = max(p.height for p in parts)
    row = Image.new('RGBA', (sum(p.width for p in parts) + 24 * (len(parts) - 1), h), (40, 40, 40, 255))
    x = 0
    for p in parts:
        row.paste(p, (x, 0), p)
        x += p.width + 24
    rows.append(row)
preview = Image.new('RGBA', (max(r.width for r in rows) + 48, sum(r.height for r in rows) + 72), (40, 40, 40, 255))
preview.paste(rows[0], (24, 24))
preview.paste(rows[1], (24, 48 + rows[0].height))
preview.save(os.path.join(ROOT, 'preview.png'))
print('preview.png written')
