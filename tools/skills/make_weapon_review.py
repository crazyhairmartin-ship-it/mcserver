"""Builds the weapon-category review page (an artifact Dylan edits) from the weapons CSV plus the pack's tools.

    python tools/skills/make_weapon_review.py <tool tags json> <out html> [mods folder]

Each row is a weapon or tool with the categories it has now; Dylan toggles categories and marks rows confirmed, and the
page stores his choices in its database (collection "weapons"). apply_weapon_review.py writes them back to the CSV.
"""
import csv
import json
import os
import re
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
CSV = PACK / 'docs' / 'superpowers' / 'specs' / '2026-10-03-weapons.csv'
TYPES = ['sword', 'light', 'two_handed', 'polearm', 'axe', 'blunt', 'scythe', 'thrown', 'bow', 'crossbow', 'magic']
TOOL_TAGS = {'minecraft:swords': ('sword', 'sword'), 'minecraft:axes': ('axe', 'axe'), 'minecraft:hoes': ('hoe', 'scythe'),
             'minecraft:pickaxes': ('pickaxe', None), 'minecraft:shovels': ('shovel', None)}


def names(mods):
    out = {}
    for jar in os.listdir(mods):
        if not jar.endswith('.jar'):
            continue
        try:
            z = zipfile.ZipFile(os.path.join(mods, jar))
        except zipfile.BadZipFile:
            continue
        for n in z.namelist():
            if re.match(r'assets/[^/]+/lang/en_us\.json$', n):
                try:
                    lang = json.loads(z.read(n).decode('utf-8', 'replace'))
                except ValueError:
                    continue
                for k, v in lang.items():
                    m = re.match(r'item\.([a-z0-9_]+)\.([a-z0-9_/]+)$', k)
                    if m and isinstance(v, str):
                        out.setdefault(m.group(1) + ':' + m.group(2), v)
    for lang_file in (PACK / 'kubejs' / 'assets').glob('*/lang/en_us.json'):     # the pack's own renames win
        for k, v in json.loads(lang_file.read_text(encoding='utf-8')).items():
            m = re.match(r'item\.([a-z0-9_]+)\.([a-z0-9_/]+)$', k)
            if m:
                out[m.group(1) + ':' + m.group(2)] = v
    return out


def _key_order(k):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', k)]


def abilities(mods, items):
    """Each item's ability text: the lang lines its class names (tooltips, right-click hints) plus lines keyed by the item id."""
    jars = {}                                   # namespace -> (zip, lang)
    for jar in os.listdir(mods):
        if not jar.endswith('.jar'):
            continue
        try:
            z = zipfile.ZipFile(os.path.join(mods, jar))
        except zipfile.BadZipFile:
            continue
        for n in z.namelist():
            m = re.match(r'assets/([^/]+)/lang/en_us\.json$', n)
            if m:
                try:
                    jars.setdefault(m.group(1), (z, json.loads(z.read(n).decode('utf-8', 'replace'))))
                except ValueError:
                    pass
    out = {}
    for it in items:
        ns, path = it['id'].split(':', 1)
        if ns not in jars:
            continue
        z, lang = jars[ns]
        keys = [k for k in lang if k.startswith(f'item.{ns}.{path}.') and not k.endswith('.desc_short')]
        cls = it.get('cls')
        if cls:
            name = next((n for n in z.namelist() if n.endswith('/' + cls + '.class')), None)
            if name:
                for k in re.findall(rb'[a-z_]+\.[a-z0-9_]+\.[a-z0-9_.]+', z.read(name)):
                    k = k.decode().rstrip('.')
                    if k in lang and ('tooltip' in k or 'rightclick' in k or k.endswith('.desc')):
                        keys.append(k)
                keys += [k for k in lang if k.startswith(f'item.{ns}.{cls.lower()}.')]
        lines = []
        for k in sorted(dict.fromkeys(keys), key=_key_order):
            v = re.sub(r'§.', '', lang[k]).replace('%%', '%')
            v = re.sub(r'%(\d+\$)?(\.\d+)?[sdf]', '#', v).strip()
            v = re.sub(r'[-꬀-꯿]', '', v).strip()    # icon glyphs from the mod's font
            if v and v not in lines and len(v) > 3:
                lines.append(v)
        if lines:
            out[it['id']] = lines
    return out


def trimmed():
    text = (PACK / 'kubejs' / 'startup_scripts' / 'trimmed_items.js').read_text(encoding='utf-8')
    return set(re.findall(r"'([a-z0-9_]+:[a-z0-9_/]+)'", text))


def rows(tool_tags, lang):
    gone = trimmed()
    items = {}
    for r in csv.DictReader(CSV.open(encoding='utf-8')):
        if r['item'] in gone:
            continue
        items[r['item']] = {'id': r['item'], 'mod': r['mod'], 'types': r['weapon types'].split(), 'tool': '',
                            'damage': r['attack damage'], 'cls': r['java class']}
    for tag, members in tool_tags.items():
        tool, implied = TOOL_TAGS[tag]
        for item in members:
            if item in gone:
                continue
            row = items.setdefault(item, {'id': item, 'mod': item.split(':')[0], 'types': [], 'tool': '', 'damage': ''})
            row['tool'] = tool
            if implied and implied not in row['types']:
                row['types'].append(implied)
    for row in items.values():
        row['name'] = lang.get(row['id'], row['id'].split(':')[1].replace('_', ' ').title())
    return sorted(items.values(), key=lambda r: (r['mod'], r['name']))


def main():
    tool_tags = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    mods = sys.argv[3] if len(sys.argv) > 3 else str(PACK.parent / 'server-test' / 'data' / 'mods')
    data = rows(tool_tags, names(mods))
    ab = abilities(mods, data)
    for row in data:
        row['ability'] = ab.get(row['id'], [])
        row.pop('cls', None)
    template = (Path(__file__).parent / 'weapon_review_template.html').read_text(encoding='utf-8')
    html = template.replace('/*DATA*/[]', json.dumps(data, ensure_ascii=False)).replace('/*TYPES*/[]', json.dumps(TYPES))
    Path(out).write_text(html, encoding='utf-8')
    print(f'{len(data)} items written to {out}')


if __name__ == '__main__':
    main()
