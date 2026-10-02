"""Ender Mail's locker restyled as a wooden birdhouse (original model, vanilla/pack textures).

Empty: just the birdhouse. Mail waiting (the block's filled=true state): a letter pokes out of the entry hole.
Every mailbox uses WOOD (Ender Mail's own blockstate already points at locker / locker_filled).
Other entries in WOODS are spare palettes: change WOOD to switch.

Writes kubejs/assets/endermail/models/block/locker{,_filled}.json. Facing north = entry hole toward -Z.
"""
import json
import os

PACK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(PACK, 'kubejs', 'assets', 'endermail')

# wood: (walls, roof, post)
WOODS = {
    'oak': ('minecraft:block/oak_planks', 'minecraft:block/spruce_planks', 'minecraft:block/stripped_oak_log'),
    'spruce': ('minecraft:block/spruce_planks', 'minecraft:block/dark_oak_planks', 'minecraft:block/stripped_spruce_log'),
    'birch': ('minecraft:block/birch_planks', 'minecraft:block/mangrove_planks', 'minecraft:block/stripped_birch_log'),
    'cherry': ('minecraft:block/cherry_planks', 'minecraft:block/dark_oak_planks', 'minecraft:block/stripped_cherry_log'),
    'dark_oak': ('minecraft:block/dark_oak_planks', 'minecraft:block/mangrove_planks', 'minecraft:block/stripped_dark_oak_log'),
    'archwood': ('ars_nouveau:block/archwood_planks', 'minecraft:block/dark_oak_planks', 'minecraft:block/stripped_spruce_log'),
    'umbran': ('biomesoplenty:block/umbran_planks', 'minecraft:block/birch_planks', 'minecraft:block/stripped_dark_oak_log'),
}
WOOD = 'oak'


def box(frm, to, tex):
    faces = {d: {'texture': '#' + tex} for d in ('north', 'south', 'east', 'west', 'up', 'down')}
    return {'from': frm, 'to': to, 'faces': faces}


BODY = [
    box([7, 0, 7], [9, 6, 9], 'post'),                 # post
    box([4.5, 6, 3.5], [11.5, 7, 12.5], 'post'),       # floor board
    box([5, 7, 4], [11, 12, 12], 'walls'),             # house
    box([6, 12, 4], [10, 13, 12], 'walls'),            # gable, in steps
    box([7, 13, 4], [9, 14, 12], 'walls'),
    box([4, 11.5, 3], [6, 12.5, 13], 'roof'),          # roof, stepped down both sides
    box([10, 11.5, 3], [12, 12.5, 13], 'roof'),
    box([5, 12.5, 3], [7, 13.5, 13], 'roof'),
    box([9, 12.5, 3], [11, 13.5, 13], 'roof'),
    box([6, 13.5, 3], [8, 14.5, 13], 'roof'),
    box([8, 13.5, 3], [10, 14.5, 13], 'roof'),
    box([7, 14.5, 3], [9, 15.5, 13], 'roof'),          # ridge
    box([7, 9, 3.9], [9, 11, 4], 'hole'),              # entry hole
    box([7.75, 7.75, 2], [8.25, 8.25, 4], 'post'),     # perch
]

LETTER = [
    box([6.75, 9.25, 2.75], [9.25, 10.75, 4.05], 'letter'),  # letter poking out of the hole
    box([7.75, 9.75, 2.7], [8.25, 10.25, 2.75], 'seal'),     # wax seal
]


def model(wood, filled):
    walls, roof, post = WOODS[wood]
    textures = {'particle': walls, 'walls': walls, 'roof': roof, 'post': post,
                'hole': 'minecraft:block/black_concrete',
                'letter': 'minecraft:block/white_wool', 'seal': 'minecraft:block/red_concrete'}
    return {'parent': 'minecraft:block/block', 'textures': textures, 'elements': BODY + (LETTER if filled else [])}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


write(os.path.join(ASSETS, 'models', 'block', 'locker.json'), model(WOOD, False))
write(os.path.join(ASSETS, 'models', 'block', 'locker_filled.json'), model(WOOD, True))
print('mailbox wood:', WOOD)
