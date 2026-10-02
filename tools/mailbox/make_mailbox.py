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
Facing north = entry hole toward -Z.
"""
import json
import os
import shutil

PACK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(PACK, 'kubejs', 'assets', 'endermail')
WOODS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'woods.json')))
assert WOODS[0]['key'] == 'oak' and len(WOODS) <= 128


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


def model(texture, filled):
    textures = {'particle': texture, 'wood': texture, 'hole': 'minecraft:block/black_concrete',
                'letter': 'minecraft:block/white_wool', 'seal': 'minecraft:block/red_concrete'}
    return {'parent': 'minecraft:block/block', 'textures': textures, 'elements': BODY + (LETTER if filled else [])}


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
