"""Corner models for Twilight Forest banisters, so they join like stairs (fotfskills BanisterBlockMixin adds the
"corner" block state: straight / inner_left / inner_right / outer_left / outer_right).

    python tools/banisters/make_banister_corners.py [path/to/twilightforest.jar]

Writes into kubejs/assets/twilightforest:
  models/block/banister_<shape>[_extended]_<corner>.json   24 shared corner models, built from TF's straight ones
  models/block/wood/banister/<wood>/<wood>_banister_..._<corner>.json   one-liners per wood (parent + planks texture)
  blockstates/<wood>_banister.json   TF's variants, each split by corner (straight keeps TF's own model)
Every Compat builds its modded-wood banisters by copying the oak banister's blockstate and models, so they pick the
corners up from these.

Geometry, in the model's own frame (facing south = rail on the south edge, z 12-16; left = counter-clockwise = east):
  inner_left  = the straight banister plus the same rail turned onto the east edge (an L)
  inner_right = the same on the west edge
  outer_left  = just the south-east corner: the rail's last 4 pixels and a corner post
  outer_right = the south-west corner
"""
import copy
import json
import re
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
OUT = PACK / 'kubejs' / 'assets' / 'twilightforest'
DEFAULT_JAR = next((PACK.parent / 'server' / 'data' / 'mods').glob('twilightforest-*.jar'), None)
SHAPES = ['tall', 'short', 'connected']
CORNERS = ['inner_left', 'inner_right', 'outer_left', 'outer_right']

# turning an element a quarter turn: the point map and how face directions follow it
TO_EAST = (lambda x, z: (z, 16 - x), {'north': 'west', 'south': 'east', 'east': 'north', 'west': 'south'})
TO_WEST = (lambda x, z: (16 - z, x), {'north': 'east', 'south': 'west', 'east': 'south', 'west': 'north'})


def is_rail(e):
    return e['from'][0] == 0 and e['to'][0] == 16


def clip_x(e, lo, hi):
    e = copy.deepcopy(e)
    e['from'][0], e['to'][0] = max(e['from'][0], lo), min(e['to'][0], hi)
    for face in e.get('faces', {}).values():
        face.pop('uv', None)                                # let the game fit the texture to the shorter rail
    return e


def turn(e, how):
    point, faces = how
    e = copy.deepcopy(e)
    (x1, z1), (x2, z2) = point(e['from'][0], e['from'][2]), point(e['to'][0], e['to'][2])
    e['from'][0], e['to'][0] = min(x1, x2), max(x1, x2)
    e['from'][2], e['to'][2] = min(z1, z2), max(z1, z2)
    new = {}
    for name, face in e.get('faces', {}).items():
        face = dict(face)
        if face.get('cullface') in faces:
            face['cullface'] = faces[face['cullface']]
        new[faces.get(name, name)] = face
    e['faces'] = new
    return e


def corner_model(base, corner):
    m = {k: v for k, v in base.items() if k != 'elements'}
    elements = base['elements']
    if corner.startswith('inner'):
        left = corner == 'inner_left'
        lo, hi = (4, 16) if left else (0, 12)               # the turned rail stops where the straight one starts
        turned = [turn(clip_x(e, lo, hi) if is_rail(e) else e, TO_EAST if left else TO_WEST) for e in elements]
        m['elements'] = copy.deepcopy(elements) + turned
    else:
        left = corner == 'outer_left'
        out = [clip_x(e, 12, 16) if left else clip_x(e, 0, 4) for e in elements if is_rail(e)]
        for e in elements:                                  # one post (and leg) pushed into the corner
            if not is_rail(e) and e['from'][0] == (10.5 if left else 2.5):
                e = copy.deepcopy(e)
                shift = 2.5 if left else -2.5
                e['from'][0] += shift
                e['to'][0] += shift
                out.append(e)
        m['elements'] = out
    return m


def main():
    jar = zipfile.ZipFile(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JAR)
    names = jar.namelist()
    read = lambda n: json.loads(jar.read(n))
    models = OUT / 'models' / 'block'
    (models).mkdir(parents=True, exist_ok=True)
    for shape in SHAPES:
        for ext in ('', '_extended'):
            base = read(f'assets/twilightforest/models/block/banister_{shape}{ext}.json')
            for corner in CORNERS:
                (models / f'banister_{shape}{ext}_{corner}.json').write_text(
                    json.dumps(corner_model(base, corner), indent=2) + '\n', encoding='utf-8')
    woods = sorted({m.group(1) for n in names if (m := re.match(r'assets/twilightforest/blockstates/(\w+)_banister\.json$', n))})
    for wood in woods:
        state = read(f'assets/twilightforest/blockstates/{wood}_banister.json')
        variants = {}
        for key, v in state['variants'].items():
            props = dict(p.split('=') for p in key.split(','))
            variants[key + ',corner=straight'] = v
            parent = 'twilightforest:block/banister_' + props['shape'] + ('_extended' if props['extended'] == 'true' else '')
            entries = v if isinstance(v, list) else [v]     # some woods pick between random plank textures
            for corner in CORNERS:
                turned = []
                for entry in entries:
                    straight = entry['model']               # twilightforest:block/wood/banister/<wood>/<wood>_banister_...
                    child = read('assets/twilightforest/models/' + straight.split(':')[1] + '.json')
                    name = f'{straight}_{corner}'
                    path = OUT / 'models' / (name.split(':')[1] + '.json')
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps({'parent': f'{parent}_{corner}', 'textures': child['textures']}, indent=2)
                                    + '\n', encoding='utf-8')
                    turned.append(dict(entry, model=name))
                variants[f'{key},corner={corner}'] = turned if isinstance(v, list) else turned[0]
        out = OUT / 'blockstates' / f'{wood}_banister.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({'variants': variants}, indent=2) + '\n', encoding='utf-8')
    print(f'{len(SHAPES) * 2 * len(CORNERS)} corner models, {len(woods)} woods: {", ".join(woods)}')


if __name__ == '__main__':
    main()
