"""Snapshot of the ids in the pack, so make_quests.py can check quests without starting the game.

    python tools/quests/make_registry.py <mods dir> <vanilla jar> [pack dir] [kubejs export dir]

<mods dir> holds the pack's mod jars (only the files named in <pack dir>/mods/*.pw.toml are read, so stray jars
don't count). <vanilla jar> is Minecraft 1.20.1's client "extra" jar (it has the assets and data), e.g.
PrismLauncher/libraries/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-extra.jar.
Writes tools/quests/registry.json: items, entities, enchantments, biomes, structures, advancements, dimensions and item/block
textures (for quest items' "texture"), plus the items
KubeJS trims out of the pack (kubejs/startup_scripts/trimmed_items.js).

Item ids come from item models, entities and enchantments from their lang keys, the rest from data files. Those
guesses aren't exact: item models include texture variants that aren't items (bountiful:bounty-rare, 2026-10-15). So
give the live server's KubeJS export too (run `kubejs export` on the server, then pass
server/data/local/kubejs/export): items, entities and enchantments then come from the real registries.
Rerun it after adding or removing mods.
"""
import json
import os
import re
import sys
import tomllib
import zipfile

ITEM_MODEL = re.compile(r'^assets/([a-z0-9_.-]+)/models/item/([a-z0-9_./-]+)\.json$')
TEXTURE = re.compile(r'^assets/([a-z0-9_.-]+)/textures/((?:item|block)/[a-z0-9_./-]+)\.png$')
LANG = re.compile(r'^assets/([a-z0-9_.-]+)/lang/en_us\.json$')
DATA = {
    'biomes': re.compile(r'^data/([a-z0-9_.-]+)/worldgen/biome/([a-z0-9_./-]+)\.json$'),
    'structures': re.compile(r'^data/([a-z0-9_.-]+)/worldgen/structure/([a-z0-9_./-]+)\.json$'),
    'advancements': re.compile(r'^data/([a-z0-9_.-]+)/advancements/([a-z0-9_./-]+)\.json$'),
    'dimensions': re.compile(r'^data/([a-z0-9_.-]+)/dimension/([a-z0-9_./-]+)\.json$'),
}


def pack_jars(mods_dir, pack_dir):
    if not pack_dir:
        return sorted(f for f in os.listdir(mods_dir) if f.endswith('.jar'))
    names = []
    for f in sorted(os.listdir(os.path.join(pack_dir, 'mods'))):
        if f.endswith('.pw.toml'):
            with open(os.path.join(pack_dir, 'mods', f), 'rb') as fh:
                names.append(tomllib.load(fh)['filename'])
    missing = [n for n in names if not os.path.exists(os.path.join(mods_dir, n))]
    if missing:
        sys.exit('missing jars (download the pack first): ' + ', '.join(missing))
    return names


def scan(jar, out):
    with zipfile.ZipFile(jar) as z:
        for name in z.namelist():
            m = ITEM_MODEL.match(name)
            if m and '/' not in m.group(2):
                out['items'].add(f'{m.group(1)}:{m.group(2)}')
                continue
            m = TEXTURE.match(name)
            if m:
                out['textures'].add(f'{m.group(1)}:{m.group(2)}')
                continue
            m = LANG.match(name)
            if m:
                try:
                    keys = json.loads(z.read(name).decode('utf-8', 'replace'))
                except ValueError:
                    continue
                for key in keys:
                    parts = key.split('.')
                    if len(parts) == 3 and parts[0] == 'entity':
                        out['entities'].add(f'{parts[1]}:{parts[2]}')
                    elif len(parts) == 3 and parts[0] == 'enchantment':
                        out['enchantments'].add(f'{parts[1]}:{parts[2]}')
                continue
            for kind, pattern in DATA.items():
                m = pattern.match(name)
                if m and not m.group(2).startswith('recipes/'):
                    out[kind].add(f'{m.group(1)}:{m.group(2)}')
                    break


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mods_dir, vanilla = sys.argv[1], sys.argv[2]
    pack_dir = sys.argv[3] if len(sys.argv) > 3 else None
    out = {k: set() for k in ('items', 'entities', 'enchantments', 'biomes', 'structures', 'advancements', 'dimensions',
                              'textures')}
    out['dimensions'].update({'minecraft:overworld', 'minecraft:the_nether', 'minecraft:the_end'})
    scan(vanilla, out)
    jars = pack_jars(mods_dir, pack_dir)
    for jar in jars:
        scan(os.path.join(mods_dir, jar), out)
    export = sys.argv[4] if len(sys.argv) > 4 else None
    if export:
        for kind, reg in (('items', 'item'), ('entities', 'entity_type'), ('enchantments', 'enchantment')):
            with open(os.path.join(export, 'registries', reg + '.json'), encoding='utf-8') as fh:
                ids = json.load(fh)
            out[kind] = set(ids if isinstance(ids, list) else ids.keys())
    root = pack_dir or os.path.join(os.path.dirname(__file__), '..', '..')
    kubejs_assets = os.path.join(root, 'kubejs', 'assets')
    for dirpath, _, files in os.walk(kubejs_assets):
        for f in files:
            rel = os.path.relpath(os.path.join(dirpath, f), kubejs_assets).replace(os.sep, '/')
            m = TEXTURE.match('assets/' + rel)
            if m:
                out['textures'].add(f'{m.group(1)}:{m.group(2)}')
    trimmed_js = os.path.join(root, 'kubejs', 'startup_scripts', 'trimmed_items.js')
    trimmed = sorted(set(re.findall(r"'([a-z0-9_.-]+:[a-z0-9_./-]+)'", open(trimmed_js).read()))) \
        if os.path.exists(trimmed_js) else []
    result = {'_about': 'Generated by tools/quests/make_registry.py from %d mod jars + vanilla 1.20.1%s. Do not edit.'
              % (len(jars), ' (items, entities, enchantments from the live KubeJS export)' if export else '')}
    result.update({k: sorted(v) for k, v in out.items()})
    result['trimmed'] = trimmed
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'registry.json')
    with open(path, 'w') as fh:
        json.dump(result, fh, indent=0, separators=(',', ':'))
        fh.write('\n')
    print('registry.json: ' + ', '.join(f'{len(v)} {k}' for k, v in result.items() if isinstance(v, list)))


if __name__ == '__main__':
    main()
