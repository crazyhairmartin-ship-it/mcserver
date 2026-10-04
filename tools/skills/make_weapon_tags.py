"""Turns docs/superpowers/specs/2026-10-03-weapons.csv into fotfskills:<type> item tags shipped in the add-on jar.

Run: python tools/skills/make_weapon_tags.py   (writes extras/fotfskills/res/data/fotfskills/tags/items/<type>.json)
Entries are optional ("required": false) so a removed mod never breaks tag loading. 'tool' rows (pickaxes, shovels)
are not a weapon type; the add-on reads #minecraft:pickaxes for Miner's Might.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
PACK = HERE.parent.parent
CSV = PACK / 'docs' / 'superpowers' / 'specs' / '2026-10-03-weapons.csv'
OUT = PACK / 'extras' / 'fotfskills' / 'res' / 'data' / 'fotfskills' / 'tags' / 'items'
TYPES = ['sword', 'light', 'two_handed', 'polearm', 'axe', 'blunt', 'scythe', 'thrown', 'bow', 'crossbow', 'magic']
VANILLA = {'scythe': ['#minecraft:hoes'], 'sword': ['#minecraft:swords'], 'axe': ['#minecraft:axes'], 'polearm': ['minecraft:trident'],
           'thrown': ['minecraft:trident'], 'bow': ['minecraft:bow'], 'crossbow': ['minecraft:crossbow']}


def build(rows):
    items = {t: [] for t in TYPES}
    for row in rows:
        for t in row['weapon types'].split():
            if t in items and row['item'] not in items[t]:
                items[t].append(row['item'])
    tags = {}
    for t in TYPES:
        values = list(VANILLA.get(t, []))
        values += [{'id': i, 'required': False} for i in sorted(items[t]) if i not in VANILLA.get(t, [])]
        tags[t] = {'replace': False, 'values': values}
    return tags


def main():
    rows = list(csv.DictReader(CSV.open(encoding='utf-8')))
    OUT.mkdir(parents=True, exist_ok=True)
    for t, tag in build(rows).items():
        (OUT / f'{t}.json').write_text(json.dumps(tag, indent=2) + '\n', encoding='utf-8')
    print(f'wrote {len(TYPES)} weapon tags to {OUT}')


if __name__ == '__main__':
    main()
