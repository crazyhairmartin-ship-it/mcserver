"""Ender Mail's locker restyled as a wooden birdhouse (original model, vanilla/pack textures).

Empty: just the birdhouse. Mail waiting (the block's filled=true state): a letter pokes out of the entry hole.
Each box is a single wood throughout. Ender Mail has one locker block, so the blockstate picks a wood per
placed position (random model list); the item in your inventory shows ITEM_WOOD.

Writes kubejs/assets/endermail/models/block/locker_<wood>{,_filled}.json, locker{,_filled}.json (item)
and kubejs/assets/endermail/blockstates/locker.json. Facing north = entry hole toward -Z.
"""
import json
import os

PACK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(PACK, 'kubejs', 'assets', 'endermail')

WOODS = {
    'oak': 'minecraft:block/oak_planks',
    'spruce': 'minecraft:block/spruce_planks',
    'birch': 'minecraft:block/birch_planks',
    'cherry': 'minecraft:block/cherry_planks',
    'dark_oak': 'minecraft:block/dark_oak_planks',
    'archwood': 'ars_nouveau:block/archwood_planks',
    'umbran': 'biomesoplenty:block/umbran_planks',
}
ITEM_WOOD = 'oak'


def box(frm, to, tex):
    faces = {d: {'texture': '#' + tex} for d in ('north', 'south', 'east', 'west', 'up', 'down')}
    return {'from': frm, 'to': to, 'faces': faces}


BODY = [
    box([7, 0, 7], [9, 6, 9], 'wood'),                 # post
    box([4.5, 6, 3.5], [11.5, 7, 12.5], 'wood'),       # floor board
    box([5, 7, 4], [11, 12, 12], 'wood'),              # house
    box([6, 12, 4], [10, 13, 12], 'wood'),             # gable, in steps
    box([7, 13, 4], [9, 14, 12], 'wood'),
    box([4, 11.5, 3], [6, 12.5, 13], 'wood'),          # roof, stepped down both sides
    box([10, 11.5, 3], [12, 12.5, 13], 'wood'),
    box([5, 12.5, 3], [7, 13.5, 13], 'wood'),
    box([9, 12.5, 3], [11, 13.5, 13], 'wood'),
    box([6, 13.5, 3], [8, 14.5, 13], 'wood'),
    box([8, 13.5, 3], [10, 14.5, 13], 'wood'),
    box([7, 14.5, 3], [9, 15.5, 13], 'wood'),          # ridge
    box([7, 9, 3.9], [9, 11, 4], 'hole'),              # entry hole
    box([7.75, 7.75, 2], [8.25, 8.25, 4], 'wood'),     # perch
]

LETTER = [
    box([6.75, 9.25, 2.75], [9.25, 10.75, 4.05], 'letter'),  # letter poking out of the hole
    box([7.75, 9.75, 2.7], [8.25, 10.25, 2.75], 'seal'),     # wax seal
]


def model(wood, filled):
    textures = {'particle': WOODS[wood], 'wood': WOODS[wood], 'hole': 'minecraft:block/black_concrete',
                'letter': 'minecraft:block/white_wool', 'seal': 'minecraft:block/red_concrete'}
    return {'parent': 'minecraft:block/block', 'textures': textures, 'elements': BODY + (LETTER if filled else [])}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


for wood in WOODS:
    for filled in (False, True):
        write(os.path.join(ASSETS, 'models', 'block', f'locker_{wood}{"_filled" if filled else ""}.json'), model(wood, filled))
write(os.path.join(ASSETS, 'models', 'block', 'locker.json'), {'parent': f'endermail:block/locker_{ITEM_WOOD}'})
write(os.path.join(ASSETS, 'models', 'block', 'locker_filled.json'), {'parent': f'endermail:block/locker_{ITEM_WOOD}_filled'})

ROTATION = {'north': 0, 'east': 90, 'south': 180, 'west': 270}
variants = {}
for facing, y in ROTATION.items():
    for filled in (False, True):
        options = []
        for wood in WOODS:
            option = {'model': f'endermail:block/locker_{wood}{"_filled" if filled else ""}'}
            if y:
                option['y'] = y
            options.append(option)
        variants[f'facing={facing},filled={str(filled).lower()}'] = options
write(os.path.join(ASSETS, 'blockstates', 'locker.json'), {'variants': variants})
print(f'{len(WOODS)} woods written')
