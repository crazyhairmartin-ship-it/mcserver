"""Recolour Regions Unexplored's mauve wood to the pack's archwood palette, keeping mauve's own designs.

    python tools/mauve/recolor_mauve.py [mods folder]

Archwood is being replaced by mauve wood (docs/superpowers/specs/2026-10-07-remove-ars-nouveau.md). Four materials
(planks, bark, stripped wood, leaves) each take the colour of their archwood counterpart: in CIELAB a pixel keeps its
offset from the mauve material's average (so grain, shading and door/trapdoor patterns stay), the average moves to
the archwood texture's average, and the lightness spread is scaled to match. Only pixels close to a material's mauve
palette change, so metal, rope and chest parts on boats and signs keep their colours. Archwood colours come from the pack's own recoloured archwood
(kubejs/assets/ars_nouveau, the #9887b6 planks) where it exists, otherwise from the Ars jar.

Writes kubejs/assets/regions_unexplored/textures/... and tools/mauve/preview.png (mauve before and after).
"""
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

PACK = Path(__file__).resolve().parents[2]
OUT = PACK / 'kubejs' / 'assets' / 'regions_unexplored' / 'textures'
OUR_ARCHWOOD = PACK / 'kubejs' / 'assets' / 'ars_nouveau' / 'textures'

# material: (mauve texture that defines it, archwood texture whose colours it takes)
MATERIALS = {
    'planks': ('block/mauve_planks.png', 'block/archwood_planks.png'),
    'bark': ('block/mauve_log.png', 'block/archwood_log.png'),             # archwood's grey bark, not its swirl
    'stripped': ('block/stripped_mauve_log.png', 'block/stripped_archwood_log.png'),
    'leaves': ('block/mauve_leaves.png', 'block/purple_archwood_leaves.png'),
}
# every mauve texture to recolour, with the materials it may contain. Only pixels close to one of those materials'
# palettes change, so the brown chest and paddles on boats (close to mauve's brown bark) are left alone.
WOOD, TREE = ('planks',), ('planks', 'bark', 'stripped', 'leaves')
TEXTURES = {
    'block/mauve_planks.png': WOOD, 'block/mauve_door_top.png': WOOD, 'block/mauve_door_bottom.png': WOOD,
    'block/mauve_trapdoor.png': WOOD, 'item/mauve_door.png': WOOD, 'item/mauve_sign.png': WOOD,
    'item/mauve_hanging_sign.png': WOOD, 'item/mauve_boat.png': WOOD, 'item/mauve_chest_boat.png': WOOD,
    'entity/boat/mauve.png': WOOD, 'entity/chest_boat/mauve.png': WOOD, 'entity/signs/mauve.png': WOOD,
    'entity/signs/hanging/mauve.png': WOOD, 'gui/hanging_signs/mauve.png': WOOD,
    'block/mauve_log.png': TREE, 'block/mauve_log_top.png': TREE, 'block/stripped_mauve_log.png': TREE,
    'block/stripped_mauve_log_top.png': TREE, 'block/mauve_leaves.png': TREE, 'block/mauve_sapling.png': TREE,
    'block/mauve_shrub_bottom.png': TREE, 'block/mauve_shrub_top.png': TREE, 'block/mauve_branch.png': TREE,
    'item/mauve_branch.png': TREE,
}
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
        self.mean_s, self.mean_t = s.mean(0), t.mean(0)
        self.scale = t[:, 0].std() / s[:, 0].std() if s[:, 0].std() > 1e-3 else 1.0

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
    ru = zipfile.ZipFile(next(mods.glob('RegionsUnexplored*.jar')))
    ars = zipfile.ZipFile(next(mods.glob('ars_nouveau*.jar')))

    def archwood(path):
        ours = OUR_ARCHWOOD / path
        if ours.exists():
            return Image.open(ours)
        return Image.open(io.BytesIO(ars.read('assets/ars_nouveau/textures/' + path)))

    def mauve(path):
        return Image.open(io.BytesIO(ru.read('assets/regions_unexplored/textures/' + path)))

    materials = {name: Material(mauve(src), archwood(arch)) for name, (src, arch) in MATERIALS.items()}
    rows = []
    for path, kinds in TEXTURES.items():
        src = mauve(path)
        new = recolor(src, [materials[k] for k in kinds])
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
    print(f'recoloured {len(rows)} mauve textures -> {OUT.relative_to(PACK)}; preview: tools/mauve/preview.png')


if __name__ == '__main__':
    main()
