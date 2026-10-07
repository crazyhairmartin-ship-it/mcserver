"""Artifacts and Spartan weapons in modded dungeon chests (YUNG's structures, When Dungeons Arise).

    python tools/loot/make_dungeon_loot.py [mods folder]

Artifacts and Spartan Weaponry only add their loot to vanilla chests, and Loot Integrations doesn't pick that up. This
writes global loot modifiers (Artifacts' own "artifacts:roll_loot_table" type, so no code is needed) that roll
- artifacts:artifact (one artifact) in ARTIFACT_CHANCE of those chests, and
- fotf:chests/dungeon_weapon (one Spartan weapon, iron > gold > diamond, worn, often enchanted) in WEAPON_CHANCE,
for every chest loot table the structure mods ship. Writes kubejs/data/fotf/{loot_tables,loot_modifiers} and
kubejs/data/forge/loot_modifiers/global_loot_modifiers.json.
"""
import json
import re
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
DATA = PACK / 'kubejs' / 'data'
STRUCTURE_JARS = ['Yungs*.jar', 'DungeonsArise*.jar']
ARTIFACT_CHANCE = 0.08
WEAPON_CHANCE = 0.15
ENCHANT_CHANCE = 0.5
MATERIALS = {'iron': 10, 'golden': 4, 'diamond': 1}
CSV = PACK / 'docs' / 'superpowers' / 'specs' / '2026-10-03-weapons.csv'


def chest_tables(mods):
    tables = []
    for pattern in STRUCTURE_JARS:
        for jar in sorted(mods.glob(pattern)):
            for n in zipfile.ZipFile(jar).namelist():
                m = re.match(r'data/([^/]+)/loot_tables/(.+)\.json$', n)
                if m and 'chests/' in m.group(2) + '/':
                    tables.append(f'{m.group(1)}:{m.group(2)}')
    return sorted(set(tables))


def spartan_weapons():
    trimmed = set(re.findall(r"'([a-z0-9_]+:[a-z0-9_/]+)'",
                             (PACK / 'kubejs' / 'startup_scripts' / 'trimmed_items.js').read_text(encoding='utf-8')))
    items = []
    for line in CSV.read_text(encoding='utf-8').splitlines()[1:]:
        item = line.split(',')[1]
        m = re.fullmatch(r'spartanweaponry:(iron|golden|diamond)_\w+', item)
        if m and item not in trimmed and not re.search(r'(arrow|bolt)', item):
            items.append((item, MATERIALS[m.group(1)]))
    return items


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def main():
    mods = Path(sys.argv[1]) if len(sys.argv) > 1 else PACK.parent / 'server-test' / 'data' / 'mods'
    tables = chest_tables(mods)
    weapons = spartan_weapons()
    write(DATA / 'fotf' / 'loot_tables' / 'chests' / 'dungeon_weapon.json', {
        'type': 'minecraft:chest',
        'pools': [{'rolls': 1, 'entries': [{'type': 'minecraft:item', 'name': item, 'weight': weight, 'functions': [
            {'function': 'minecraft:set_damage', 'damage': {'type': 'minecraft:uniform', 'min': 0.5, 'max': 0.9}},
            {'function': 'minecraft:enchant_with_levels', 'levels': {'type': 'minecraft:uniform', 'min': 5, 'max': 25},
             'treasure': False, 'conditions': [{'condition': 'minecraft:random_chance', 'chance': ENCHANT_CHANCE}]},
        ]} for item, weight in weapons]}]})
    any_table = {'condition': 'minecraft:any_of',
                 'terms': [{'condition': 'forge:loot_table_id', 'loot_table_id': t} for t in tables]}
    for name, table, chance in (('dungeon_artifacts', 'artifacts:artifact', ARTIFACT_CHANCE),
                                ('dungeon_weapons', 'fotf:chests/dungeon_weapon', WEAPON_CHANCE)):
        write(DATA / 'fotf' / 'loot_modifiers' / f'{name}.json', {
            'type': 'artifacts:roll_loot_table', 'lootTable': table,
            'conditions': [any_table, {'condition': 'minecraft:random_chance', 'chance': chance}]})
    write(DATA / 'forge' / 'loot_modifiers' / 'global_loot_modifiers.json',
          {'replace': False, 'entries': ['fotf:dungeon_artifacts', 'fotf:dungeon_weapons']})
    print(f'{len(tables)} structure chest tables, {len(weapons)} Spartan weapons in the pool')


if __name__ == '__main__':
    main()
