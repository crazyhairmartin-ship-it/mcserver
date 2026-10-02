"""Birdhouse mailboxes (Ender Mail's locker) in every wood, for the fotfmail add-on.

Each box is one wood throughout. The fotfmail add-on (extras/fotfmail) gives the locker a "wood" block state;
the crafting recipe (kubejs/server_scripts/mail_recipes.js) sets it from the planks used, and breaking the
mailbox keeps it (loot table copy_state). A letter pokes out of the entry hole when mail is waiting (filled=true).

Input: tools/mailbox/woods.json (key, planks item, planks texture), built from the server's #minecraft:planks
minus trimmed items, oak first (oak is the default state and the plain item).

Writes:
  extras/fotfmail/src/fotfmail/MailboxWood.java         wood enum (block state values, in this order)
  kubejs/assets/endermail/blockstates/locker.json       facing x filled x wood
  kubejs/assets/endermail/models/block/locker_<wood>{,_filled}.json
  kubejs/assets/endermail/models/item/locker.json       per-wood overrides (predicate fotfmail:wood = index/128)
  kubejs/data/endermail/loot_tables/blocks/locker.json  keeps the wood when broken
  kubejs/startup_scripts/mailbox_woods.js               global.MAILBOX_WOODS for recipes and tooltips
Facing north = entry hole toward -Z. The model is 1.5 blocks tall (house on a long fence-width post).
"""
import json
import os
import shutil

PACK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(PACK, 'kubejs', 'assets', 'endermail')
WOODS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'woods.json')))
assert WOODS[0]['key'] == 'oak' and len(WOODS) <= 128


def box(frm, to, tex):
    """An element with explicit UVs. Minecraft's automatic UVs come from the element's position in the block, which
    runs off the texture for parts above y 16; parts up there take their UVs as if 8px lower instead."""
    (x0, y0, z0), (x1, y1, z1) = frm, to
    if y1 > 16:
        y0, y1 = y0 - 8, y1 - 8
    uvs = {
        'north': [16 - x1, 16 - y1, 16 - x0, 16 - y0],
        'south': [x0, 16 - y1, x1, 16 - y0],
        'east': [16 - z1, 16 - y1, 16 - z0, 16 - y0],
        'west': [z0, 16 - y1, z1, 16 - y0],
        'up': [x0, z0, x1, z1],
        'down': [x0, 16 - z1, x1, 16 - z0],
    }
    faces = {d: {'texture': '#' + tex, 'uv': [round(v, 3) for v in uv]} for d, uv in uvs.items()}
    return {'from': frm, 'to': to, 'faces': faces}


BODY = [
    box([6, 0, 6], [10, 13, 10], 'wood'),              # post, as thick as a fence post (mailbox is 1.5 blocks tall)
    box([3.5, 13, 2.5], [12.5, 14, 13.5], 'wood'),       # floor board
    box([4, 14, 3], [12, 20, 13], 'wood'),              # house
    box([5, 20, 3], [11, 21, 13], 'wood'),             # gable, in steps
    box([6, 21, 3], [10, 22, 13], 'wood'),
    box([7, 22, 3], [9, 23, 13], 'wood'),
    box([3, 19.5, 2], [5, 20.5, 14], 'wood'),          # roof, stepped down both sides
    box([11, 19.5, 2], [13, 20.5, 14], 'wood'),
    box([4, 20.5, 2], [6, 21.5, 14], 'wood'),
    box([10, 20.5, 2], [12, 21.5, 14], 'wood'),
    box([5, 21.5, 2], [7, 22.5, 14], 'wood'),
    box([9, 21.5, 2], [11, 22.5, 14], 'wood'),
    box([6, 22.5, 2], [8, 23.5, 14], 'wood'),
    box([8, 22.5, 2], [10, 23.5, 14], 'wood'),
    box([7, 23.5, 2], [9, 24, 14], 'wood'),            # ridge
    box([6.5, 16, 2.9], [9.5, 18.5, 3], 'hole'),        # entry hole
    box([7.75, 15, 1], [8.25, 15.5, 3], 'wood'),         # perch
]

LETTER = [
    box([6.25, 16.5, 1.75], [9.75, 18, 3.05], 'letter'),     # letter poking out of the hole
    box([7.75, 17, 1.7], [8.25, 17.5, 1.75], 'seal'),         # wax seal
]


# The model is 1.5 blocks tall, so it's shrunk a little in inventories, item frames and on the ground.
DISPLAY = {
    'gui': {'rotation': [30, 225, 0], 'translation': [0, -2.5, 0], 'scale': [0.42, 0.42, 0.42]},
    'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.18, 0.18, 0.18]},
    'fixed': {'rotation': [0, 0, 0], 'translation': [0, -2, 0], 'scale': [0.35, 0.35, 0.35]},
    'thirdperson_righthand': {'rotation': [75, 45, 0], 'translation': [0, 1.5, 0], 'scale': [0.3, 0.3, 0.3]},
    'firstperson_righthand': {'rotation': [0, 45, 0], 'translation': [0, 0, 0], 'scale': [0.3, 0.3, 0.3]},
    'firstperson_lefthand': {'rotation': [0, 225, 0], 'translation': [0, 0, 0], 'scale': [0.3, 0.3, 0.3]},
}


def model(texture, filled):
    textures = {'particle': texture, 'wood': texture, 'hole': 'minecraft:block/black_concrete',
                'letter': 'minecraft:block/white_wool', 'seal': 'minecraft:block/red_concrete'}
    return {'parent': 'minecraft:block/block', 'textures': textures, 'elements': BODY + (LETTER if filled else []),
            'display': DISPLAY}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        if isinstance(obj, str):
            f.write(obj)
        else:
            json.dump(obj, f, indent=1)


shutil.rmtree(os.path.join(ASSETS, 'models'), ignore_errors=True)
for w in WOODS:
    for filled in (False, True):
        write(os.path.join(ASSETS, 'models', 'block', f'locker_{w["key"]}{"_filled" if filled else ""}.json'),
              model(w['texture'], filled))

ROTATION = {'north': 0, 'east': 90, 'south': 180, 'west': 270}
variants = {}
for facing, y in ROTATION.items():
    for filled in (False, True):
        for w in WOODS:
            variant = {'model': f'endermail:block/locker_{w["key"]}{"_filled" if filled else ""}'}
            if y:
                variant['y'] = y
            variants[f'facing={facing},filled={str(filled).lower()},wood={w["key"]}'] = variant
write(os.path.join(ASSETS, 'blockstates', 'locker.json'), {'variants': variants})

write(os.path.join(ASSETS, 'models', 'item', 'locker.json'), {
    'parent': 'endermail:block/locker_oak',
    'overrides': [{'predicate': {'fotfmail:wood': i / 128}, 'model': f'endermail:block/locker_{w["key"]}'}
                  for i, w in enumerate(WOODS) if i],
})

write(os.path.join(PACK, 'kubejs', 'data', 'endermail', 'loot_tables', 'blocks', 'locker.json'), {
    'type': 'minecraft:block',
    'pools': [{
        'rolls': 1,
        'entries': [{'type': 'minecraft:item', 'name': 'endermail:locker',
                     'functions': [{'function': 'minecraft:copy_state', 'block': 'endermail:locker',
                                    'properties': ['wood']}]}],
        'conditions': [{'condition': 'minecraft:survives_explosion'}],
    }],
})

enum_values = ',\n'.join(f'    {w["key"].upper()}("{w["key"]}")' for w in WOODS)
write(os.path.join(PACK, 'extras', 'fotfmail', 'src', 'fotfmail', 'MailboxWood.java'), f'''package fotfmail;

import net.minecraft.util.StringRepresentable;

/** Mailbox woods: generated by tools/mailbox/make_mailbox.py from tools/mailbox/woods.json. Oak first (default). */
public enum MailboxWood implements StringRepresentable {{
{enum_values};

    private final String name;

    MailboxWood(String name) {{
        this.name = name;
    }}

    @Override
    public String m_7912_() {{
        return name;
    }}
}}
''')

js_woods = ',\n'.join(f"  ['{w['key']}', '{w['planks']}']" for w in WOODS)
write(os.path.join(PACK, 'kubejs', 'startup_scripts', 'mailbox_woods.js'), f'''// Mailbox woods: [block state value, planks]. Generated by tools/mailbox/make_mailbox.py; must match the
// fotfmail add-on's MailboxWood enum (extras/fotfmail), so regenerate both together.
global.MAILBOX_WOODS = [
{js_woods}
]
''')
print(f'{len(WOODS)} woods written')
