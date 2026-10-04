"""Gives items that share a display name with another mod's item a "(Mod Name)" tag, e.g. "Oak Chair (Handcrafted)".

Reads every mod jar's en_us lang file, skips items the pack hides (trimmed items and the extra copies in
kubejs/startup_scripts/duplicate_groups.js), and writes the tagged names into kubejs/assets/<mod>/lang/en_us.json
next to any hand-written overrides. Run it again after adding or removing mods:

    python tools/names/make_name_tags.py [mods folder, default ../server/data/mods]
"""
import json
import os
import re
import sys
import zipfile
from collections import defaultdict

PACK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
MANAGED = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'managed_keys.json')

# Short names players know the mods by (anything missing falls back to the jar's displayName)
MOD_NAMES = {
    'another_furniture': 'Another Furniture', 'furniture': 'Refurbished', 'handcrafted': 'Handcrafted',
    'candlelight': 'Candlelight', 'biomesoplenty': "Biomes O' Plenty", 'regions_unexplored': 'Regions Unexplored',
    'bloomingnature': 'Blooming Nature', 'farmersdelight': "Farmer's Delight", 'farm_and_charm': 'Farm & Charm',
    'alexsmobs': "Alex's Mobs", 'alexscaves': "Alex's Caves", 'irons_spellbooks': "Iron's Spells",
    'irons_lib': "Iron's Lib", 'irons_patreon_lib': "Iron's Patreon", 'crittersandcompanions': 'Critters & Companions',
    'friendsandfoes': 'Friends & Foes', 'mowziesmobs': "Mowzie's Mobs", 'lilis_lucky_lures': "Lili's Lucky Lures",
    'wildernature': 'Wilder Nature', 'twilightforest': 'Twilight Forest', 'beachparty': 'Beach Party',
    'herbalbrews': 'Herbal Brews', 'nethervinery': 'Nether Vinery', 'snowyspirit': 'Snowy Spirit',
    'rainbowreef': 'Rainbow Reef', 'smallships': 'Small Ships', 'immersive_aircraft': 'Immersive Aircraft',
    'guardvillagers': 'Guard Villagers', 'simplyswords': 'Simply Swords', 'grapplemod': 'Reforged',
    'parcool': 'ParCool', 'paraglider': 'Paragliders', 'ars_nouveau': 'Ars Nouveau', 'mimi': 'MIMI',
    'geckolib': 'GeckoLib', 'meadow': 'Meadow', 'camping': 'Camping', 'brewery': 'Brewery', 'bakery': 'Bakery',
    'vinery': 'Vinery', 'cataclysm': 'Cataclysm', 'aquaculture': 'Aquaculture', 'butterflies': 'Butterflies',
}

# Names many items share on purpose (the tooltip tells them apart)
SKIP_NAMES = {'musicdisc', 'discfragment'}


def norm(name):
    return re.sub(r'[^a-z]', '', name.lower())


def clashes(names, hidden):
    """names: {lang key: (item id, name)} -> groups of (item id, lang key, name) whose name another mod also uses."""
    by_name = defaultdict(list)
    for key, (item_id, name) in names.items():
        if item_id not in hidden and norm(name) not in SKIP_NAMES:
            by_name[norm(name)].append((item_id, key, name))
    groups = [sorted(g) for g in by_name.values() if len({i.split(':')[0] for i, _, _ in g}) > 1]
    return sorted(groups, key=lambda g: g[0][2])


def tag_names(groups, mod_names):
    """{lang key: "Name (Mod)"} for every item in every clash group."""
    out = {}
    for group in groups:
        for item_id, key, name in group:
            ns = item_id.split(':')[0]
            mod = MOD_NAMES.get(ns) or re.sub(r'^\[.*?\] *', '', mod_names.get(ns, '')) or ns.replace('_', ' ').title()
            out[key] = f'{name} ({mod})'
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
    return hidden, set(js_list(trimmed, 'TINKERS_KEEP'))


def read_jars(mods):
    names, mod_names = {}, {}
    for jar in sorted(os.listdir(mods)):
        if not jar.endswith('.jar'):
            continue
        try:
            z = zipfile.ZipFile(os.path.join(mods, jar))
        except zipfile.BadZipFile:
            continue
        for n in z.namelist():
            if n == 'META-INF/mods.toml':
                toml = z.read(n).decode('utf-8', 'replace')
                for mod_id, display in re.findall(r'modId\s*=\s*"([^"]+)".*?displayName\s*=\s*"([^"]+)"', toml, re.S):
                    mod_names.setdefault(mod_id, display)
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
    return names, mod_names


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
    names, mod_names = read_jars(mods)
    hidden, tinkers_keep = hidden_items()
    hidden |= {i for i, _ in names.values() if i.startswith('tconstruct:') and i not in tinkers_keep}
    previous = json.load(open(MANAGED)) if os.path.exists(MANAGED) else []
    for key, value in hand_written(previous).items():  # the pack's own renames are the names players see
        if key in names:
            names[key] = (names[key][0], value)
    tagged = tag_names(clashes(names, hidden), mod_names)

    by_ns = defaultdict(dict)
    for key, value in tagged.items():
        by_ns[key.split('.')[1]][key] = value
    for ns in set(by_ns) | {k.split('.')[1] for k in previous}:
        path = os.path.join(PACK, 'kubejs', 'assets', ns, 'lang', 'en_us.json')
        lang = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
        lang = {k: v for k, v in lang.items() if k not in previous}  # drop our old tags, keep hand-written keys
        lang.update(by_ns.get(ns, {}))
        if lang:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(dict(sorted(lang.items())), f, indent=2, ensure_ascii=False)
                f.write('\n')
        elif os.path.exists(path):
            os.remove(path)
    with open(MANAGED, 'w', newline='\n') as f:
        json.dump(sorted(tagged), f, indent=0)
        f.write('\n')
    print(f'{len(tagged)} names tagged across {len(by_ns)} mods')


if __name__ == '__main__':
    main()
