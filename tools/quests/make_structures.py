"""Lists every structure in the pack and whether it generates, for planning quests around the world.

    python tools/quests/make_structures.py <mods dir> <vanilla jar> [pack dir]

Same inputs as make_registry.py. Reads every structure, structure set and biome tag from vanilla, the pack's mod jars
(only those named in mods/*.pw.toml) and the pack's own datapack overrides (kubejs/data), then applies the Towns and
Towers on/off config and Lithostitched worldgen modifiers (how CTOV adds its villages). Writes:
  tools/quests/structures.json    one entry per structure: mod, dimension(s), biomes, set, spacing, generates or not
  docs/world-structures.md        the same as readable tables, grouped by dimension and mod

A structure generates when a structure set places it and nothing switches it off. Spacing is the structure set's
average distance between attempts, in chunks (bigger = rarer). Structures in no set are pieces of other structures,
or only made by commands or other structures.
"""
import json
import os
import re
import sys
import tomllib
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
KINDS = {
    'structure': re.compile(r'^data/([a-z0-9_.-]+)/worldgen/structure/([a-z0-9_./-]+)\.json$'),
    'structure_set': re.compile(r'^data/([a-z0-9_.-]+)/worldgen/structure_set/([a-z0-9_./-]+)\.json$'),
    'biome_tag': re.compile(r'^data/([a-z0-9_.-]+)/tags/worldgen/biome/([a-z0-9_./-]+)\.json$'),
    'biome': re.compile(r'^data/([a-z0-9_.-]+)/worldgen/biome/([a-z0-9_./-]+)\.json$'),
    'modifier': re.compile(r'^data/([a-z0-9_.-]+)/lithostitched/worldgen_modifier/([a-z0-9_./-]+)\.json$'),
}
NETHER = {'minecraft:nether_wastes', 'minecraft:soul_sand_valley', 'minecraft:crimson_forest',
          'minecraft:warped_forest', 'minecraft:basalt_deltas'}
END = {'minecraft:the_end', 'minecraft:end_highlands', 'minecraft:end_midlands', 'minecraft:small_end_islands',
       'minecraft:end_barrens'}
MOD_NAMES = {
    'minecraft': 'Vanilla', 'cataclysm': "L_Ender's Cataclysm", 'mowziesmobs': "Mowzie's Mobs",
    'twilightforest': 'Twilight Forest', 'irons_spellbooks': "Iron's Spells", 'alexscaves': "Alex's Caves",
    'friendsandfoes': 'Friends & Foes', 'dungeons_arise': 'When Dungeons Arise',
    'dungeons_arise_seven_seas': 'When Dungeons Arise: Seven Seas', 'nova_structures': 'Dungeons & Taverns',
    'ctov': "ChoiceTheorem's Overhauled Village", 't_and_t': 'Towns and Towers', 'towns_and_towers': 'Towns and Towers',
    'betterdungeons': "YUNG's Better Dungeons", 'bettermineshafts': "YUNG's Better Mineshafts",
    'betterdeserttemples': "YUNG's Better Desert Temples", 'betterjungletemples': "YUNG's Better Jungle Temples",
    'betterwitchhuts': "YUNG's Better Witch Huts", 'betteroceanmonuments': "YUNG's Better Ocean Monuments",
    'betterfortresses': "YUNG's Better Nether Fortresses", 'betterstrongholds': "YUNG's Better Strongholds",
    'betterendisland': "YUNG's Better End Island", 'yungsbridges': "YUNG's Bridges", 'yungsextras': "YUNG's Extras",
    'structory': 'Structory', 'structory_towers': 'Structory: Towers', 'mvs': "Moog's Voyager Structures",
    'mns': "Moog's Nether Structures", 'mes': "Moog's End Structures", 'mos': "Moog's Ocean Structures",
    'mss': "Moog's Soaring Structures", 'skyvillages': 'Sky Villages', 'artifacts': 'Artifacts',
    'naturalist': 'Naturalist', 'regions_unexplored': 'Regions Unexplored', 'nullscape': 'Nullscape',
    'bountiful': 'Bountiful', 'realmrpg_skeletons': 'Realm RPG: Fallen Adventurers', 'aquaculture': 'Aquaculture',
    'immersive_aircraft': 'Immersive Aircraft', 'smallships': 'Small Ships', 'supplementaries': 'Supplementaries',
}


def pack_jars(mods_dir, pack_dir):
    names = []
    for f in sorted(os.listdir(os.path.join(pack_dir, 'mods'))):
        if f.endswith('.pw.toml'):
            with open(os.path.join(pack_dir, 'mods', f), 'rb') as fh:
                names.append(tomllib.load(fh)['filename'])
    return [os.path.join(mods_dir, n) for n in names if os.path.exists(os.path.join(mods_dir, n))]


def read_sources(vanilla, jars, pack_dir):
    """Every data file by kind and id, as a list of (source, json) in load order (pack datapack last)."""
    files = {k: {} for k in KINDS}
    skipped = []

    def add(kind, ident, source, text):
        data = lenient_json(text)
        if data is None:
            skipped.append(f'{source}: {kind} {ident}')
            return
        files[kind].setdefault(ident, []).append((source, data))

    for jar in [vanilla] + jars:
        with zipfile.ZipFile(jar) as z:
            for name in z.namelist():
                for kind, pattern in KINDS.items():
                    m = pattern.match(name)
                    if m:
                        add(kind, f'{m.group(1)}:{m.group(2)}', os.path.basename(jar), z.read(name).decode('utf-8', 'replace'))
                        break
    base = os.path.join(pack_dir, 'kubejs')
    for dirpath, _, filenames in os.walk(os.path.join(base, 'data')):
        for f in filenames:
            rel = os.path.relpath(os.path.join(dirpath, f), base).replace(os.sep, '/')
            for kind, pattern in KINDS.items():
                m = pattern.match(rel)
                if m:
                    with open(os.path.join(dirpath, f), encoding='utf-8') as fh:
                        add(kind, f'{m.group(1)}:{m.group(2)}', 'pack (kubejs/data)', fh.read())
                    break
    if skipped:
        print(f'could not read {len(skipped)} files, e.g. ' + '; '.join(skipped[:3]))
    return files


def lenient_json(text):
    """JSON the way Minecraft reads it: also allows comments and trailing commas."""
    try:
        return json.loads(text)
    except ValueError:
        pass
    cleaned = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    cleaned = re.sub(r'(?m)^\s*//.*$|(?<=[,{\[\s])//[^\n"]*$', '', cleaned)
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    try:
        return json.loads(cleaned)
    except ValueError:
        return None


def resolve_tags(tag_files):
    """Biome tags with references expanded; a later file with "replace": true starts the tag over."""
    raw = {}
    for ident, versions in tag_files.items():
        values = []
        for _, data in versions:
            if data.get('replace'):
                values = []
            for v in data.get('values', []):
                values.append(v if isinstance(v, str) else v.get('id', ''))
        raw[ident] = values
    cache = {}

    def expand(ident, seen=()):
        if ident in cache:
            return cache[ident]
        out = set()
        for v in raw.get(ident, []):
            if v.startswith('#'):
                if v[1:] not in seen:
                    out |= expand(v[1:], seen + (ident,))
            else:
                out.add(v)
        cache[ident] = out
        return out

    return {ident: expand(ident) for ident in raw}


def dimension_of(biome, tags):
    if biome in NETHER or any(biome in tags.get(t, ()) for t in ('minecraft:is_nether', 'forge:is_nether', 'c:is_nether')):
        return 'Nether'
    if biome in END or any(biome in tags.get(t, ()) for t in ('minecraft:is_end', 'forge:is_end', 'c:is_end')):
        return 'End'
    if biome.startswith('twilightforest:'):
        return 'Twilight Forest'
    return 'Overworld'


def towns_and_towers_disabled(pack_dir):
    path = os.path.join(pack_dir, 'config', 'towns_and_towers', 'structure_enable_or_disable_new.json5')
    if not os.path.exists(path):
        return set()
    text = open(path, encoding='utf-8').read()
    return {m.group(1) for m in re.finditer(r'"([a-z0-9_]+)"\s*:\s*false', text)}


def rarity(placement):
    kind = placement.get('type', '')
    if kind.endswith('concentric_rings'):
        return 'rings', f"{placement.get('count', '?')} in rings"
    if kind.startswith('twilightforest:'):
        return 'fixed grid', 'Twilight grid'
    spacing = placement.get('spacing')
    if not isinstance(spacing, int):
        return 'unknown', '?'
    freq = placement.get('frequency', 1.0)
    # frequency thins the grid by area, so the effective spacing grows with its square root
    eff = spacing / freq ** 0.5 if freq else spacing
    label = ('very common' if eff <= 12 else 'common' if eff <= 24 else 'uncommon' if eff <= 40
             else 'rare' if eff <= 80 else 'very rare')
    extra = f' x{freq:g}' if freq != 1.0 else ''
    return label, f'{spacing}{extra}'


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mods_dir, vanilla = sys.argv[1], sys.argv[2]
    pack_dir = sys.argv[3] if len(sys.argv) > 3 else ROOT
    files = read_sources(vanilla, pack_jars(mods_dir, pack_dir), pack_dir)
    tags = resolve_tags(files['biome_tag'])
    tt_off = towns_and_towers_disabled(pack_dir)

    sets = {set_id: (versions[-1][1].get('placement', {}),
                     [e.get('structure') for e in versions[-1][1].get('structures', []) if e.get('structure')])
            for set_id, versions in files['structure_set'].items()}
    # Lithostitched worldgen modifiers (CTOV uses them to add its villages and outposts to vanilla's sets)
    for _, versions in files['modifier'].items():
        data = versions[-1][1]
        kind = data.get('type', '')
        targets = data.get('structure_sets', [])
        targets = [targets] if isinstance(targets, str) else targets
        for set_id in targets:
            if set_id not in sets:
                continue
            if kind == 'lithostitched:add_structure_set_entries':
                sets[set_id][1].extend(e.get('structure') for e in data.get('entries', []) if e.get('structure'))
            elif kind == 'lithostitched:remove_structure_set_entries':
                gone = set(data.get('structures', []))
                sets[set_id] = (sets[set_id][0], [x for x in sets[set_id][1] if x not in gone])
    placed = {}   # structure -> (set id, placement, set size)
    for set_id, (placement, members) in sets.items():
        for sid in members:
            placed.setdefault(sid, (set_id, placement, len(members)))

    reg_path = os.path.join(pack_dir, 'tools', 'quests', 'registry.json')
    known_biomes = set(json.load(open(reg_path)).get('biomes', [])) if os.path.exists(reg_path) else set()
    out = {}
    for sid, versions in sorted(files['structure'].items()):
        source, data = versions[-1]
        biomes_field = data.get('biomes', [])
        if isinstance(biomes_field, str):
            biome_label = biomes_field
            biomes = tags.get(biomes_field[1:], set()) if biomes_field.startswith('#') else {biomes_field}
        else:
            biome_label = ', '.join(biomes_field[:4]) + (' ...' if len(biomes_field) > 4 else '')
            biomes = set()
            for b in biomes_field:
                biomes |= tags.get(b[1:], set()) if b.startswith('#') else {b}
        biomes = {b for b in biomes if b in known_biomes} or biomes   # tags may name optional biomes of absent mods
        dims = sorted({dimension_of(b, tags) for b in biomes}) or ['?']
        ns, path = sid.split(':', 1)
        status, why = 'no', 'not in any structure set (a piece, or made another way)'
        set_id, spacing, rar = '', '', ''
        if sid in placed:
            set_id, placement, size = placed[sid]
            rar, spacing = rarity(placement)
            status, why = 'yes', ''
            if not biomes:
                status, why = 'no', 'no biomes it can generate in'
            if ns in ('t_and_t', 'towns_and_towers') and path.split('/')[-1] in tt_off:
                status, why = 'no', 'switched off in config/towns_and_towers'
        out[sid] = {'mod': MOD_NAMES.get(ns, ns), 'dimensions': dims, 'biomes': biome_label, 'biome_count': len(biomes),
                    'set': set_id, 'spacing': spacing, 'rarity': rar, 'generates': status == 'yes', 'why_not': why,
                    'type': data.get('type', ''), 'overridden_by_pack': source.startswith('pack')}

    lm_path = os.path.join(pack_dir, 'tools', 'quests', 'src', 'landmarks.json')
    landmarks = json.load(open(lm_path)) if os.path.exists(lm_path) else {}
    for sid, v in out.items():
        v['name'] = landmarks.get('names', {}).get(sid, '')
    for sid, by in landmarks.get('replaced_by', {}).items():
        if sid in out:
            out[sid].update(generates=False, why_not=f'replaced by {by} (switched off in its code)')
    for sid, note in landmarks.get('seen_in_world', {}).items():
        if sid in out and not out[sid]['generates']:
            out[sid].update(generates=True, seen_in_world=note)

    with open(os.path.join(ROOT, 'tools', 'quests', 'structures.json'), 'w') as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write('\n')

    gen = {k: v for k, v in out.items() if v['generates']}
    lines = ['# World structures', '',
             f'Generated by `tools/quests/make_structures.py` from the pack\'s jars and overrides. '
             f'{len(out)} structures in total; **{len(gen)} generate** in new chunks. Rarity is from the structure '
             'set\'s spacing in chunks (very common <=12, common <=24, uncommon <=40, rare <=80, very rare above; '
             'a frequency below 1 thins the grid, counted as spacing / sqrt(frequency)). "Rings" are placed in rings around spawn (strongholds); '
             '"fixed grid" is the Twilight Forest\'s own layout, where each landmark has its set place in the grid.', '',
             'Quest start points and how to use each kind of structure: see the "Structures as quest start points" '
             'section of `docs/superpowers/specs/2026-10-13-boss-progression.md`.', '']
    for dim in ('Overworld', 'Nether', 'End', 'Twilight Forest'):
        rows = {k: v for k, v in gen.items() if dim in v['dimensions']}
        if not rows:
            continue
        lines += [f'## {dim} ({len(rows)})', '']
        by_mod = {}
        for k, v in rows.items():
            by_mod.setdefault(v['mod'], []).append((k, v))
        for mod in sorted(by_mod):
            lines += [f'### {mod}', '', '| Structure | Rarity (spacing) | Where | Set |', '|---|---|---|---|']
            for k, v in sorted(by_mod[mod]):
                where = v['biomes'] + (f' ({v["biome_count"]} biomes)' if v['biome_count'] > 1 else '')
                label = f'`{k}`' + (f' ({v["name"]})' if v['name'] else '')
                rar = f'{v["rarity"]} ({v["spacing"]})' + (' **seen in the world, config says off**' if v.get('seen_in_world') else '')
                lines.append(f'| {label} | {rar} | {where} | `{v["set"]}` |')
            lines.append('')
    feats = landmarks.get('features', {})
    if feats:
        lines += [f'## Placed as world features, not structures ({len(feats)})', '',
                  'Landmarks a structure search won\'t find; quests reach them with a biome, place or checkmark task.', '']
        lines += [f'- {f["name"]}' for f in feats.values()] + ['']
    off = {k: v for k, v in out.items() if not v['generates'] and v['why_not'] != 'not in any structure set (a piece, or made another way)'}
    lines += [f'## Present but switched off ({len(off)})', '', '| Structure | Why |', '|---|---|']
    lines += [f'| `{k}` | {v["why_not"]} |' for k, v in sorted(off.items())]
    pieces = [k for k, v in out.items() if v['why_not'].startswith('not in any')]
    lines += ['', f'## Not placed by a structure set ({len(pieces)})', '',
              'Pieces of bigger structures or ones made another way (summoned, from items or other structures): '
              + ', '.join(f'`{k}`' for k in sorted(pieces)), '']
    os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
    with open(os.path.join(ROOT, 'docs', 'world-structures.md'), 'w') as fh:
        fh.write('\n'.join(lines))
    print(f'{len(out)} structures, {len(gen)} generate; ' + ', '.join(
        f'{d}: {sum(1 for v in gen.values() if d in v["dimensions"])}' for d in ('Overworld', 'Nether', 'End', 'Twilight Forest')))


if __name__ == '__main__':
    main()
