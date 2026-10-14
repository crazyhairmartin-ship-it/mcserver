"""What's actually inside each structure, so puzzle quests are built on blocks that really exist there.

    python tools/quests/make_structure_contents.py <mods dir> <vanilla jar> [pack dir]

Same inputs as make_registry.py. For every jigsaw structure (most modded ones, villages, YUNG's), follows its start
pool through every template pool its pieces' jigsaw blocks point to, and reads each piece's .nbt. Writes
tools/quests/src/structure_contents.json:

  "dungeons_arise:bandit_towers": {"pieces": 26, "blocks": {"minecraft:chest": 14, ...}, "entities": {...}}

Numbers are how many of the structure's possible pieces contain that block or entity at least once (a structure is
built from some of its pieces, so "3 of 26" means "sometimes, in a few rooms"). Only blocks worth building a quest
step around are listed: containers, bells, levers, buttons, plates, lecterns, campfires, candles, heads, banners,
signs, spawners, beds, flowers in pots and the like. Structures that aren't jigsaw (vanilla temples, igloos, mansions,
some mods' hardcoded ones) are listed with "pieces": 0: check those in game.
"""
import collections
import glob
import gzip
import json
import os
import re
import struct
import sys
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'tools', 'quests', 'src', 'structure_contents.json')
INTEREST = re.compile(r'(chest|barrel|shulker|bell|lever|button|pressure_plate|tripwire|lectern|campfire|brazier|'
                      r'candle|lantern|skull|head|banner|sign|spawner|dispenser|dropper|target|beacon|bed$|'
                      r'potted_|flower_pot|anvil|cauldron|brewing_stand|enchanting_table|jukebox|bookshelf|'
                      r'altar|pedestal|shrine|statue|urn|vase|decorated_pot|suspicious_|respawn_anchor|lodestone|'
                      r'note_block|crafting_table|furnace|smoker|grindstone|stonecutter|loom|cartography|smithing|'
                      r'fletching|composter|bee_nest|beehive|cake|end_portal_frame|conduit|lightning_rod|bookcase)')


def read_nbt(raw):
    b = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
    pos = [0]

    def u(fmt, n):
        v = struct.unpack(fmt, b[pos[0]:pos[0] + n])[0]
        pos[0] += n
        return v

    def rd(t):
        if t == 1: return u('>b', 1)
        if t == 2: return u('>h', 2)
        if t == 3: return u('>i', 4)
        if t == 4: return u('>q', 8)
        if t == 5: return u('>f', 4)
        if t == 6: return u('>d', 8)
        if t == 7: n = u('>i', 4); pos[0] += n; return None
        if t == 8: n = u('>H', 2); s = b[pos[0]:pos[0] + n].decode('utf-8', 'replace'); pos[0] += n; return s
        if t == 9:
            et = u('>b', 1); n = u('>i', 4)
            return [rd(et) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                tt = u('>b', 1)
                if tt == 0:
                    return d
                n = u('>H', 2); k = b[pos[0]:pos[0] + n].decode('utf-8', 'replace'); pos[0] += n
                d[k] = rd(tt)
        if t == 11: n = u('>i', 4); pos[0] += 4 * n; return None
        if t == 12: n = u('>i', 4); pos[0] += 8 * n; return None
        raise ValueError(f'bad tag {t}')

    t = u('>b', 1)
    n = u('>H', 2)
    pos[0] += n
    return rd(t)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mods_dir, vanilla = sys.argv[1], sys.argv[2]
    pack = sys.argv[3] if len(sys.argv) > 3 else ROOT
    wanted = set()
    for f in glob.glob(os.path.join(pack, 'mods', '*.pw.toml')):
        m = re.search(r'^filename = "(.+)"', open(f, encoding='utf-8').read(), re.M)
        if m:
            wanted.add(m.group(1))
    jars = [vanilla] + [os.path.join(mods_dir, j) for j in sorted(os.listdir(mods_dir)) if j in wanted]
    files = {}   # path inside data -> (zipfile, name); later jars override earlier, like datapacks
    for jar in jars:
        try:
            z = zipfile.ZipFile(jar)
        except (OSError, zipfile.BadZipFile):
            continue
        for name in z.namelist():
            if name.startswith('data/') and (name.endswith('.json') or name.endswith('.nbt')):
                files[name] = (z, name)
    kjs = os.path.join(pack, 'kubejs', 'data')
    for path in glob.glob(os.path.join(kjs, '**', '*'), recursive=True):
        if os.path.isfile(path) and (path.endswith('.json') or path.endswith('.nbt')):
            files['data/' + os.path.relpath(path, kjs).replace(os.sep, '/')] = (None, path)

    def load(path):
        z, name = files[path]
        return z.read(name) if z else open(name, 'rb').read()

    def rl(ident):
        ns, _, p = ident.partition(':') if ':' in ident else ('minecraft', '', ident)
        return ns, p

    piece_cache = {}

    def piece(location):
        if location in piece_cache:
            return piece_cache[location]
        ns, p = rl(location)
        info = None
        for folder in ('structures', 'structure'):
            path = f'data/{ns}/{folder}/{p}.nbt'
            if path in files:
                try:
                    d = read_nbt(load(path))
                except Exception:
                    break
                palette = d.get('palette') or ((d.get('palettes') or [[]])[0])
                names = [s.get('Name', '') for s in palette]
                used = set()
                pools = set()
                for blk in d.get('blocks', []):
                    st = blk.get('state')
                    if st is None or st >= len(names):
                        continue
                    used.add(names[st])
                    if names[st] == 'minecraft:jigsaw' and isinstance(blk.get('nbt'), dict):
                        pool = blk['nbt'].get('pool')
                        if pool and pool != 'minecraft:empty':
                            pools.add(pool)
                ents = {e.get('nbt', {}).get('id', '?') for e in d.get('entities', []) if isinstance(e.get('nbt'), dict)}
                info = ({n for n in used if INTEREST.search(n.split(':')[-1])}, ents, pools)
                break
        piece_cache[location] = info
        return info

    def pool_elements(pool):
        ns, p = rl(pool)
        path = f'data/{ns}/worldgen/template_pool/{p}.json'
        if path not in files:
            return []
        try:
            d = json.loads(load(path))
        except ValueError:
            return []
        out = []

        def walk(el):
            if not isinstance(el, dict):
                return
            if 'location' in el and isinstance(el['location'], str):
                out.append(el['location'])
            for k in ('element', 'elements'):
                v = el.get(k)
                if isinstance(v, list):
                    for x in v:
                        walk(x)
                elif isinstance(v, dict):
                    walk(v)
        for e in d.get('elements', []):
            walk(e)
        return out

    result = {}
    for path in sorted(files):
        m = re.match(r'^data/([a-z0-9_.-]+)/worldgen/structure/([a-z0-9_./-]+)\.json$', path)
        if not m:
            continue
        sid = f'{m.group(1)}:{m.group(2)}'
        try:
            d = json.loads(load(path))
        except ValueError:
            continue
        start = d.get('start_pool')
        if not isinstance(start, str):
            result[sid] = {'pieces': 0, 'blocks': {}, 'entities': {}}
            continue
        seen_pools, todo, pieces = set(), [start], set()
        while todo and len(seen_pools) < 400:
            pool = todo.pop()
            if pool in seen_pools:
                continue
            seen_pools.add(pool)
            for loc in pool_elements(pool):
                if loc in pieces:
                    continue
                pieces.add(loc)
                info = piece(loc)
                if info:
                    todo.extend(info[2] - seen_pools)
        blocks, ents = collections.Counter(), collections.Counter()
        real = 0
        for loc in pieces:
            info = piece(loc)
            if not info:
                continue
            real += 1
            blocks.update(info[0])
            ents.update(info[1])
        result[sid] = {'pieces': real, 'blocks': dict(sorted(blocks.items(), key=lambda kv: (-kv[1], kv[0]))),
                       'entities': dict(sorted(ents.items(), key=lambda kv: (-kv[1], kv[0])))}
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('{\n"_about": "Generated by tools/quests/make_structure_contents.py. Per structure: how many of its '
                 'possible pieces contain each block/entity. pieces 0 = not a jigsaw structure, check in game.",\n')
        fh.write(',\n'.join(json.dumps(k) + ': ' + json.dumps(v, separators=(',', ':')) for k, v in result.items()))
        fh.write('\n}\n')
    jig = sum(1 for v in result.values() if v['pieces'])
    print(f'structure_contents.json: {len(result)} structures, {jig} with pieces read')


if __name__ == '__main__':
    main()
