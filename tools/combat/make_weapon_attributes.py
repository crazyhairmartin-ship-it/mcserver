"""Give every categorised weapon that has no Better Combat data of its own a Better Combat move set.

    python tools/combat/make_weapon_attributes.py [mods folder]

Reads the weapon categories (docs/superpowers/specs/2026-10-03-weapons.csv, the same ones the Attack tree uses) and
writes kubejs/data/<mod>/weapon_attributes/<item>.json for each melee weapon whose mod (or Better Combat itself) ships
no weapon_attributes file for it. The preset follows the categories, and two_handed is set from ours, so Better
Combat's two-handed rule (no off-hand item) matches the skills' two-handed perks. Where a weapon's own mod already
has Better Combat data, the mod's two-handed setting wins: the weapon's row in the CSV is updated to match (run
tools/skills/make_weapon_tags.py afterwards). Bows, crossbows, thrown-only weapons, tools and magic-only items keep
their normal swing.
"""
import csv
import json
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
CSV = PACK / 'docs' / 'superpowers' / 'specs' / '2026-10-03-weapons.csv'
OUT = PACK / 'kubejs' / 'data'
MARK = 'fotf_generated'          # every file we write carries this key, so a rerun only clears its own files


def preset(types):
    """Weapon categories -> Better Combat preset (bettercombat:<name>), or None to keep the vanilla swing."""
    two = 'two_handed' in types
    if 'scythe' in types:
        return 'scythe'
    if 'polearm' in types and 'axe' in types:
        return 'halberd'
    if 'polearm' in types and 'blunt' in types:
        return 'hammer' if two else 'mace'
    if 'polearm' in types:
        return 'spear' if two else 'trident'
    if 'axe' in types:
        return 'double_axe' if two else 'axe'
    if 'blunt' in types:
        return 'hammer' if two else 'mace'
    if 'sword' in types:
        return 'claymore' if two else 'sword'
    if 'light' in types:
        return 'dagger'
    return None


def covered(mods):
    """weapon_attributes shipped by the mods and Better Combat: id (incl. sub-folders like base/greatsword) -> json."""
    have = {}
    for jar in Path(mods).glob('*.jar'):
        try:
            names = zipfile.ZipFile(jar).namelist()
        except zipfile.BadZipFile:
            continue
        for n in names:
            parts = n.split('/')
            if len(parts) >= 4 and parts[0] == 'data' and parts[2] == 'weapon_attributes' and n.endswith('.json'):
                try:
                    have[f'{parts[1]}:{"/".join(parts[3:])[:-5]}'] = json.loads(zipfile.ZipFile(jar).read(n))
                except ValueError:
                    pass
    return have


def two_handed(have, data, depth=0):
    """Whether Better Combat treats this weapon as two-handed, following its parent chain."""
    attrs = data.get('attributes', {})
    if 'two_handed' in attrs:
        return bool(attrs['two_handed'])
    parent = data.get('parent')
    return two_handed(have, have.get(parent, {}), depth + 1) if parent and depth < 8 else False


def main():
    mods = sys.argv[1] if len(sys.argv) > 1 else str(PACK.parent / 'server-test' / 'data' / 'mods')
    have = covered(mods)
    for old in OUT.glob('*/weapon_attributes/*.json'):
        if MARK in json.loads(old.read_text(encoding='utf-8')):
            old.unlink()
    written, synced, by_preset = 0, [], {}
    with open(CSV, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    for row in rows:
        item = row['item']
        types = row['weapon types'].split()
        if ':' not in item:
            continue
        if item in have:                                # the mod's own move set and two-handed setting win
            theirs = two_handed(have, have[item])
            if theirs != ('two_handed' in types):
                types = [t for t in types if t != 'two_handed'] + (['two_handed'] if theirs else [])
                row['weapon types'] = ' '.join(types)
                synced.append(f"{item}: {'two-handed' if theirs else 'one-handed'}")
            continue
        name = preset(set(types))
        if not name:
            continue
        ns, path = item.split(':', 1)
        target = OUT / ns / 'weapon_attributes' / f'{path}.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({MARK: True, 'parent': f'bettercombat:{name}',
                                      'attributes': {'two_handed': 'two_handed' in types}}, indent=2) + '\n',
                          encoding='utf-8')
        written += 1
        by_preset[name] = by_preset.get(name, 0) + 1
    if synced:
        with open(CSV, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader()
            w.writerows(rows)
    print(f'{written} weapons given a Better Combat move set; {len(synced)} categories changed to match their mod:')
    for line in synced:
        print('  ' + line)
    for name, n in sorted(by_preset.items(), key=lambda x: -x[1]):
        print(f'  {name}: {n}')


if __name__ == '__main__':
    main()
