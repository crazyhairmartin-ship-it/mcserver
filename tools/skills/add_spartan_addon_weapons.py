"""Categorise Spartan Weaponry add-on weapons (Twilight Forest, Cataclysm...) like the base Spartan weapon of the same type.

    python tools/skills/add_spartan_addon_weapons.py [mods folder]

Every add-on item named <material>_<type> (spartantwilight:steeleaf_longsword) gets the weapon types of
spartanweaponry:iron_<type> from docs/superpowers/specs/2026-10-03-weapons.csv, so the Attack tree perks and the
"damage with your skills" tooltip cover it. Items already in the CSV are left alone. Then run make_weapon_tags.py
(and tools/combat/make_weapon_attributes.py for Better Combat).
"""
import csv
import json
import re
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
CSV = PACK / 'docs' / 'superpowers' / 'specs' / '2026-10-03-weapons.csv'
ADDONS = ['spartantwilight', 'spartancataclysm']


def main():
    mods = Path(sys.argv[1]) if len(sys.argv) > 1 else PACK.parent / 'server-test' / 'data' / 'mods'
    with open(CSV, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    have = {r['item'] for r in rows}
    types = {}
    for r in rows:
        m = re.fullmatch(r'spartanweaponry:(?:iron|wooden|stone|golden|diamond|netherite)_(\w+)', r['item'])
        if m and m.group(1) not in types:
            types[m.group(1)] = r['weapon types']
    added = []
    for jar in mods.glob('*.jar'):
        try:
            z = zipfile.ZipFile(jar)
        except zipfile.BadZipFile:
            continue
        for ns in ADDONS:
            lang = f'assets/{ns}/lang/en_us.json'
            if lang not in z.namelist():
                continue
            for key in json.loads(z.read(lang)):
                if not key.startswith(f'item.{ns}.') or key.count('.') != 2:
                    continue
                path = key.split('.')[2]
                kind = next((t for t in sorted(types, key=len, reverse=True) if path.endswith('_' + t)), None)
                item = f'{ns}:{path}'
                if kind and item not in have:
                    rows.append({**{k: '' for k in fields}, 'mod': ns, 'item': item, 'weapon types': types[kind]})
                    have.add(item)
                    added.append(item)
    with open(CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(f'added {len(added)} add-on weapons to the categories')
    for item in added:
        print('  ' + item)


if __name__ == '__main__':
    main()
