"""Ender Mail's package drawn as a little chest with a stamp slapped on its lid, crooked (vanilla + pack textures).

Writes kubejs/assets/endermail/models/block/package.json and stamped_package.json (the same chest; a sent package
also gets string tied around it both ways). The block's shape/occlusion fix is in the fotfmail add-on (PackageBlockMixin).
Facing north = latch toward -Z. The package screen's GUI texture is made by make_package_gui.py (needs Pillow).
"""
import json
import os

PACK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(PACK, 'kubejs', 'assets', 'endermail', 'models', 'block')


def box(frm, to, tex, faces=('north', 'south', 'east', 'west', 'up', 'down'), rotation=None, uv=None):
    element = {'from': frm, 'to': to, 'faces': {d: {'texture': '#' + tex} for d in faces}}
    if uv:
        for face in element['faces'].values():
            face['uv'] = uv
    if rotation:
        element['rotation'] = rotation
    return element


CHEST = [
    box([1, 0, 1], [15, 9, 15], 'wood'),                       # body
    box([1, 9, 1], [15, 14, 15], 'wood'),                      # lid
    box([0.9, 8.6, 0.9], [15.1, 9.4, 15.1], 'trim'),           # band around the lid seam
    box([7, 7, 0.4], [9, 11, 1], 'latch'),                     # latch on the front
    # the stamp, stuck on crooked and off-centre on the lid
    box([3.5, 14, 6], [9.5, 14.02, 12], 'stamp', faces=('up',), uv=[0, 0, 16, 16],
        rotation={'origin': [6.5, 14, 9], 'axis': 'y', 'angle': 22.5}),
]

STRING = [                                                   # string tied around a package that's been sent
    box([7.6, 0, 0.8], [8.4, 14.08, 1], 'string'),             # front to back
    box([7.6, 0, 15], [8.4, 14.08, 15.2], 'string'),
    box([7.6, 14.04, 1], [8.4, 14.08, 15], 'string'),
    box([0.8, 0, 7.6], [1, 14.1, 8.4], 'string'),               # left to right, crossing on the lid
    box([15, 0, 7.6], [15.2, 14.1, 8.4], 'string'),
    box([1, 14.06, 7.6], [15, 14.1, 8.4], 'string'),
]

TEXTURES = {
    'particle': 'minecraft:block/oak_planks',
    'wood': 'minecraft:block/oak_planks',
    'trim': 'minecraft:block/dark_oak_planks',
    'latch': 'minecraft:block/iron_block',
    'stamp': 'endermail:item/stamp',
    'string': 'minecraft:block/white_wool',
}

os.makedirs(OUT, exist_ok=True)
for name, elements in (('package', CHEST), ('stamped_package', CHEST + STRING)):
    with open(os.path.join(OUT, name + '.json'), 'w') as f:
        json.dump({'parent': 'minecraft:block/block', 'textures': TEXTURES, 'elements': elements}, f, indent=1)
print('package models written')
