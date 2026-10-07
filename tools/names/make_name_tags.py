"""Gives items that share a display name with another mod's item a name of their own (furniture excluded).

The names live in tools/names/names.json:
- "species": a tree or stone word swapped across one mod's whole set, e.g. Regions Unexplored "Maple" -> "Sugar Maple"
  (only items whose id starts with that word, optionally after stripped_/potted_).
- "renames": single items by id, mostly named after what they're crafted from.

Reads every mod jar's en_us lang file, writes the new names into kubejs/assets/<mod>/lang/en_us.json next to any
hand-written overrides, and lists clashes that are still left. Run it again after adding or removing mods:

    python tools/names/make_name_tags.py [mods folder, default ../server/data/mods]
"""
import json
import os
import re
import sys
import zipfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.normpath(os.path.join(HERE, '..', '..'))
MANAGED = os.path.join(HERE, 'managed_keys.json')
NAMES = os.path.join(HERE, 'names.json')

# Furniture keeps its names (Dylan: same-named furniture is fine)
FURNITURE_MODS = {'another_furniture', 'handcrafted', 'furniture'}
FURNITURE = re.compile(r'chair|table|stool|bench|sofa|shelf|cabinet|drawer|lamp|curtain|cupboard|counter|desk|wardrobe|'
                       r'shutter|sideboard|nightstand|couch|dresser|\bbed\b|sleeping bag|hammock|chest|bookcase|crate|'
                       r'basket|flower box|flower pot|planter|pillow|cushion|carpet|lantern|chandelier', re.I)

# Names many items share on purpose (the tooltip tells them apart), or that aren't real items
SKIP_NAMES = {'', 'musicdisc', 'discfragment', 'bannerpattern', 'patreonstatue'}


def norm(name):
    return re.sub(r'[^a-z]', '', name.lower())


def is_furniture(item_id, name):
    return item_id.split(':')[0] in FURNITURE_MODS or bool(FURNITURE.search(name))


def clashes(names, hidden):
    """names: {lang key: (item id, name)} -> groups of (item id, lang key, name) whose name another mod also uses."""
    by_name = defaultdict(list)
    for key, (item_id, name) in names.items():
        if item_id not in hidden and norm(name) not in SKIP_NAMES and not is_furniture(item_id, name):
            by_name[norm(name)].append((item_id, key, name))
    groups = [sorted(g) for g in by_name.values() if len({i.split(':')[0] for i, _, _ in g}) > 1]
    return sorted(groups, key=lambda g: g[0][2])


def rename(names, spec):
    """{lang key: new name} from the species swaps and single renames in spec."""
    out = {}
    for key, (item_id, name) in names.items():
        ns, path = item_id.split(':')
        new = name
        if is_furniture(item_id, name):
            continue
        for swap in spec['species']:
            token = swap['word'].lower().replace(' ', '_')
            if swap['mod'] == ns and re.match(r'(stripped_|potted_)?' + re.escape(token) + r'(_|$)', path):
                new = re.sub(r'\b' + re.escape(swap['word']) + r'\b', swap['to'], new)
        new = spec['renames'].get(item_id, new)
        if new != name:
            out[key] = new
    return out


def js_list(text, var):
    m = re.search(r'global\.' + var + r'\s*=\s*\[(.*?)\n\]', text, re.S)
    return re.findall(r"'([a-z0-9_]+:[a-z0-9_/]+)'", m.group(1)) if m else []


def hidden_items():
    scripts = os.path.join(PACK, 'kubejs', 'startup_scripts')
    trimmed = open(os.path.join(scripts, 'trimmed_items.js'), encoding='utf-8').read()
    dupes = open(os.path.join(scripts, 'duplicate_groups.js'), encoding='utf-8').read()
    hidden = set(js_list(trimmed, 'TRIMMED_ITEMS')) | set(js_list(dupes, 'HIDDEN_ITEMS'))
    for items in re.findall(r'items: \[([^\]]*)\]', dupes):
        hidden |= set(re.findall(r"'([^']+)'", items)[1:])
    return hidden


def read_jars(mods):
    names = {}
    for jar in sorted(os.listdir(mods)):
        if not jar.endswith('.jar'):
            continue
        try:
            z = zipfile.ZipFile(os.path.join(mods, jar))
        except zipfile.BadZipFile:
            continue
        for n in z.namelist():
            if not re.match(r'assets/[^/]+/lang/en_us\.json$', n):
                continue
            try:
                lang = json.loads(z.read(n).decode('utf-8', 'replace'))
            except ValueError:
                continue
            for key, value in lang.items():
                m = re.match(r'(item|block)\.([a-z0-9_]+)\.([a-z0-9_]+)$', key)
                if m and m.group(2) != 'minecraft' and isinstance(value, str):
                    names.setdefault(key, (m.group(2) + ':' + m.group(3), value))
    return names


def hand_written(previous):
    out = {}
    assets = os.path.join(PACK, 'kubejs', 'assets')
    for ns in os.listdir(assets):
        path = os.path.join(assets, ns, 'lang', 'en_us.json')
        if os.path.exists(path):
            out.update({k: v for k, v in json.load(open(path, encoding='utf-8')).items() if k not in previous})
    return out


def main():
    mods = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PACK, '..', 'server', 'data', 'mods')
    names = read_jars(mods)
    hidden = hidden_items()
    hidden |= set(json.load(open(NAMES, encoding='utf-8')).get('skip', []))
    previous = json.load(open(MANAGED)) if os.path.exists(MANAGED) else []
    for key, value in hand_written(previous).items():  # the pack's own renames are the names players see
        if key in names:
            names[key] = (names[key][0], value)
    renamed = rename(names, json.load(open(NAMES, encoding='utf-8')))

    by_ns = defaultdict(dict)
    for key, value in renamed.items():
        by_ns[key.split('.')[1]][key] = value
    for ns in set(by_ns) | {k.split('.')[1] for k in previous}:
        path = os.path.join(PACK, 'kubejs', 'assets', ns, 'lang', 'en_us.json')
        lang = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
        lang = {k: v for k, v in lang.items() if k not in previous}  # drop our old names, keep hand-written keys
        lang.update(by_ns.get(ns, {}))
        if lang:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(dict(sorted(lang.items())), f, indent=2, ensure_ascii=False)
                f.write('\n')
        elif os.path.exists(path):
            os.remove(path)
            for d in (os.path.dirname(path), os.path.dirname(os.path.dirname(path))):
                if not os.listdir(d):
                    os.rmdir(d)
    with open(MANAGED, 'w', newline='\n') as f:
        json.dump(sorted(renamed), f, indent=0)
        f.write('\n')
    print(f'{len(renamed)} names written across {len(by_ns)} mods')

    left = clashes({k: (i, renamed.get(k, n)) for k, (i, n) in names.items()}, hidden)
    for group in left:
        print('still clashing: ' + ' | '.join(f'{i} ({n})' for i, _, n in group))


if __name__ == '__main__':
    main()
