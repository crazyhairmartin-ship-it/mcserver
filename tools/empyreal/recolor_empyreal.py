"""Recolour Biomes O' Plenty's empyreal wood halfway towards the pack's archwood palette, keeping empyreal's designs.

    python tools/empyreal/recolor_empyreal.py [mods folder]

Archwood is being replaced by empyreal wood (docs/superpowers/specs/2026-10-07-remove-ars-nouveau.md). Only the inner
wood changes: planks and everything made from them (doors, trapdoors, signs, boats), the log ends' inner rings and
stripped logs. Bark and leaves keep empyreal's own colours. In CIELAB a pixel keeps its offset from empyreal's plank
average (so grain, shading and door/trapdoor patterns stay), and the average moves BLEND of the way to the archwood
planks' average (#9887b6, kubejs/assets/ars_nouveau). Only pixels close to empyreal's inner-wood palette change, so
bark rings, metal, rope and chest parts keep their colours.

Writes kubejs/assets/biomesoplenty/textures/... and tools/empyreal/preview.png (empyreal before and after).
"""
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

PACK = Path(__file__).resolve().parents[2]
OUT = PACK / 'kubejs' / 'assets' / 'biomesoplenty' / 'textures'
OUR_ARCHWOOD = PACK / 'kubejs' / 'assets' / 'ars_nouveau' / 'textures'

BLEND = 0.5         # how far empyreal moves towards archwood: 0 = unchanged, 1 = archwood's colour
# material: (empyreal texture that defines it, archwood texture whose colours it moves towards)
MATERIALS = {
    'planks': ('block/empyreal_planks.png', 'block/archwood_planks.png'),
    'stripped': ('block/stripped_empyreal_log.png', 'block/archwood_planks.png'),
}
TEXTURES = ['block/empyreal_planks.png', 'block/empyreal_door_top.png', 'block/empyreal_door_bottom.png',
            'block/empyreal_trapdoor.png', 'block/empyreal_log_top.png', 'block/stripped_empyreal_log.png',
            'block/stripped_empyreal_log_top.png', 'item/empyreal_door.png', 'item/empyreal_sign.png',
            'item/empyreal_hanging_sign.png', 'item/empyreal_boat.png', 'item/empyreal_chest_boat.png',
            'entity/boat/empyreal.png', 'entity/chest_boat/empyreal.png', 'entity/signs/empyreal.png',
            'entity/signs/hanging/empyreal.png', 'gui/hanging_signs/empyreal.png']
MATCH = 12.0        # max CIELAB distance from a material's palette for a pixel to count as that material


def srgb_to_lab(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab_to_srgb(lab):
    fy = (lab[..., 0] + 16) / 116
    fx, fz = fy + lab[..., 1] / 500, fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787) * np.array([0.95047, 1.0, 1.08883])
    m = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])
    c = np.clip(xyz @ m.T, 0, 1)
    c = np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)
    return np.round(c * 255).astype(np.uint8)


def lab_pixels(img):
    """Lab colours of the opaque pixels (first frame for animated textures)."""
    a = np.asarray(img.convert('RGBA')).astype(float)
    a = a[:a.shape[1]] if a.shape[0] > a.shape[1] else a
    return srgb_to_lab(a[..., :3])[a[..., 3] > 0]


class Material:
    def __init__(self, src, target):
        s, t = lab_pixels(src), lab_pixels(target)
        self.palette = np.unique(np.round(s, 1), axis=0)
        self.mean_s = s.mean(0)
        self.mean_t = self.mean_s + BLEND * (t.mean(0) - self.mean_s)
        full = t[:, 0].std() / s[:, 0].std() if s[:, 0].std() > 1e-3 else 1.0
        self.scale = 1 + BLEND * (full - 1)

    def distance(self, lab):
        """Distance from each pixel to the nearest colour of this material's palette."""
        d = np.linalg.norm(lab[..., None, :] - self.palette, axis=-1)
        return d.min(-1)

    def apply(self, lab):
        out = lab - self.mean_s
        out[..., 0] *= self.scale
        return out + self.mean_t


def recolor(src, materials):
    a = np.asarray(src.convert('RGBA')).astype(float)
    lab = srgb_to_lab(a[..., :3])
    dists = np.stack([m.distance(lab) for m in materials], -1)
    best = dists.argmin(-1)
    out = lab.copy()
    for i, m in enumerate(materials):
        hit = (best == i) & (dists[..., i] <= MATCH) & (a[..., 3] > 0)
        out[hit] = m.apply(lab[hit])
    return Image.fromarray(np.concatenate([lab_to_srgb(out), a[..., 3:].astype(np.uint8)], -1), 'RGBA')


def main():
    mods = Path(sys.argv[1]) if len(sys.argv) > 1 else PACK.parent / 'server' / 'data' / 'mods'
    bop = zipfile.ZipFile(next(mods.glob('BiomesOPlenty*.jar')))
    ars = zipfile.ZipFile(next(mods.glob('ars_nouveau*.jar')))

    def archwood(path):
        ours = OUR_ARCHWOOD / path
        if ours.exists():
            return Image.open(ours)
        return Image.open(io.BytesIO(ars.read('assets/ars_nouveau/textures/' + path)))

    def empyreal(path):
        return Image.open(io.BytesIO(bop.read('assets/biomesoplenty/textures/' + path)))

    materials = [Material(empyreal(src), archwood(arch)) for src, arch in MATERIALS.values()]
    rows = []
    for path in TEXTURES:
        src = empyreal(path)
        new = recolor(src, materials)
        (OUT / path).parent.mkdir(parents=True, exist_ok=True)
        new.save(OUT / path)
        rows.append((src, new))

    def tile(img):
        img = img.convert('RGBA')
        img = img.crop((0, 0, img.width, min(img.height, img.width)))       # first frame of animations
        scale = max(1, 64 // max(img.size))
        return img.resize((img.width * scale, img.height * scale), Image.NEAREST)

    cells = [[tile(x) for x in r] for r in rows]
    w = max(c.width for r in cells for c in r) + 8
    h = max(c.height for r in cells for c in r) + 8
    sheet = Image.new('RGBA', (w * 2, h * len(cells)), (40, 40, 40, 255))
    for y, r in enumerate(cells):
        for x, c in enumerate(r):
            sheet.alpha_composite(c, (x * w + 4, y * h + 4))
    sheet.save(Path(__file__).parent / 'preview.png')
    print(f'recoloured {len(rows)} empyreal textures -> {OUT.relative_to(PACK)}; preview: tools/empyreal/preview.png')


if __name__ == '__main__':
    main()
