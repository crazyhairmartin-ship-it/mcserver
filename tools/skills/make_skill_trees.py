"""Turns tools/skills/trees.json into Pufferfish's Skills config (config/puffish_skills/).

Run: python tools/skills/make_skill_trees.py

XP: tools/skills/xp.json -> categories/<id>/experience.json (curve, level cap, sources; fotfskills:* types come
from the add-on). Rewards: tools/skills/perks.json -> each rank definition's "rewards" (phase 2a: attributes).
Node ids must stay <slug>_<k>: the add-on's client mixin groups ranks by that pattern.

Layout: one tile per node. A node's ranks are separate Pufferfish skills stacked on the same tile and chained
(rank 2 needs rank 1); the fotfskills add-on draws a stack as one tile with an "n/total" counter. Each tier row
starts with a roman-numeral tile ("Tier 3 · 10 points") and choice tiers get an "OR" tile between the branches.
Label and OR tiles are skills with no connections, so they can never be unlocked.
"""
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).parent
PACK = HERE.parent.parent
OUT = PACK / 'config' / 'puffish_skills'
ICONS = json.loads((HERE / 'icons.json').read_text(encoding='utf-8'))
TILE = 30           # pixels between tiles in a row
ROW_HEIGHT = 34     # pixels between tier rows
NUMERALS = 'fotfskills:textures/gui/skills/'   # tier_<n>.png and or.png, drawn by extras/fotfskills/draw_numerals.py
PER_RANK = re.compile(r'^(?P<clause>.*?) per rank(?P<tail>.*)$')
AMOUNT = re.compile(r'(?P<sign>[+-]?)(?P<num>\d+(?:\.\d+)?)(?P<unit>%?)')


def load(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def slug(name):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', name.lower().replace("'", ''))).strip('_')


def base_name(name):
    """Icon key: 'Prospector II' shares Prospector's icon."""
    return re.sub(r' II$', '', name)


def rank_ids(node):
    return [f'{slug(node["name"])}_{k}' for k in range(1, node['r'] + 1)]


def frame(node):
    kind = 'challenge' if node['cap'] else 'goal' if node['b'] else 'task'
    return {'type': 'advancement', 'data': {'frame': kind}}


def fmt(value):
    return f'{value:.2f}'.rstrip('0').rstrip('.')


def rank_text(node, k):
    """The effect a node has with k ranks, e.g. '+8% mining speed' for Stone Sense rank 2.

    In the clause before "per rank", every signed or percent amount scales with k ('+1 armour', '8% faster');
    plain numbers ('for 30 s', 'spend 5 mana', 'Y 40') stay fixed. A clause with no signed or percent amount
    scales its first number ('reaches 4 blocks further'). The add-on's tooltip shows the owned rank's text in
    white and the next rank's in grey.
    """
    m = PER_RANK.match(node['d'])
    if node['r'] == 1 or not m:
        return node['d']
    amounts = list(AMOUNT.finditer(m['clause']))
    if not amounts:
        return node['d']
    scaled = [a for a in amounts if a['sign'] or a['unit']] or amounts[:1]
    clause = m['clause']
    for a in reversed(scaled):
        text = f'{a["sign"]}{fmt(float(a["num"]) * k)}{a["unit"]}'
        clause = clause[:a.start()] + text + clause[a.end():]
    return f'{clause}{m["tail"]}'.strip()


def extras(node, tree):
    """Extra tooltip line: choice partner and prerequisite (shown in its own colour by the add-on)."""
    parts = []
    if node['b']:
        others = [o['name'] for o in tree['nodes'] if o['t'] == node['t'] and o['b'] and o['b'] != node['b']]
        parts.append(f'Pick one: this or {" / ".join(others)}.')
    if node['needs']:
        parts.append(f'Needs {node["needs"]} (all ranks).')
    return ' '.join(parts)


def marker(title, text, texture, req):
    return {'title': title, 'description': text, 'icon': {'type': 'texture', 'data': {'texture': NUMERALS + texture}},
            'frame': {'type': 'advancement', 'data': {'frame': 'task'}}, 'required_spent_points': req}


def build_category(tree, tiers, xp=None, perks=None):
    req = {t['n']: t['req'] for t in tiers}
    by_name = {n['name']: n for n in tree['nodes']}
    icons = ICONS[tree['id']]
    definitions, skills = {}, {}
    uni, exclusive = [], []
    rows = {}
    for n in tree['nodes']:
        rows.setdefault(n['t'], []).append(n)
    for tier_n, row in rows.items():
        choice = any(n['b'] for n in row)
        # tiles in this row: label, then nodes, with an OR tile before the first B-branch node
        tiles = [('label', None)]
        for n in row:
            if n['b'] == 'B' and ('or', None) not in tiles:
                tiles.append(('or', None))
            tiles.append(('node', n))
        x0 = -(len(tiles) - 1) * TILE // 2
        y = (tier_n - 1) * ROW_HEIGHT
        for i, (kind, n) in enumerate(tiles):
            x = x0 + i * TILE
            if kind == 'label':
                sid = f'tier_{tier_n}_label'
                points = 'Start' if req[tier_n] == 0 else f'{req[tier_n]} points'
                text = ('Open from the start.' if req[tier_n] == 0 else
                        f'Opens once you have spent {req[tier_n]} points in this tree.')
                if choice:
                    text += ' Pick one branch: taking one locks the other.'
                definitions[sid] = marker(f'Tier {tier_n} · {points}', text, f'tier_{tier_n}.png', req[tier_n])
                skills[sid] = {'x': x, 'y': y, 'definition': sid}
                continue
            if kind == 'or':
                sid = f'tier_{tier_n}_or'
                definitions[sid] = marker('OR', 'Pick one of the two branches beside this; taking one locks the other.',
                                          'or.png', req[tier_n])
                skills[sid] = {'x': x, 'y': y, 'definition': sid}
                continue
            ids = rank_ids(n)
            for k, sid in enumerate(ids, start=1):
                definitions[sid] = {
                    'title': n['name'],
                    'description': rank_text(n, k),
                    'icon': {'type': 'item', 'data': {'item': icons.get(base_name(n['name']), tree['icon'])}},
                    'frame': frame(n),
                    'cost': n['c'],
                    'required_spent_points': req[n['t']],
                }
                if extras(n, tree):
                    definitions[sid]['extra_description'] = extras(n, tree)
                skills[sid] = {'x': x, 'y': y, 'definition': sid}
                if k == 1 and not n['needs']:
                    skills[sid]['root'] = True
                if k > 1:
                    uni.append([ids[k - 2], sid])
    for n in tree['nodes']:
        if n['needs']:
            uni.append([rank_ids(by_name[n['needs']])[-1], rank_ids(n)[0]])
    for tier_n, row in rows.items():
        a = [rank_ids(n)[0] for n in row if n['b'] == 'A']
        b = [rank_ids(n)[0] for n in row if n['b'] == 'B']
        exclusive += [[x, y] for x in a for y in b]
    category = {
        'title': tree['name'],
        'description': f'Earns XP from: {tree["xp"]}',
        'icon': {'type': 'item', 'data': {'item': tree['icon']}},
        'background': tree['background'],
        'unlocked_by_default': True,
        'exclusive_root': False,
        'starting_points': 0,
    }
    connections = {'normal': {'unidirectional': uni}, 'exclusive': {'bidirectional': exclusive}}
    files = {'category.json': category, 'definitions.json': definitions, 'skills.json': skills,
             'connections.json': connections}
    if xp is not None:
        files['experience.json'] = {
            'level_limit': xp['level_limit'],
            'experience_per_level': {'type': 'expression', 'data': {'expression': xp['curve']}},
            'sources': xp['sources'][tree['id']],
        }
    return files


def write_config(data, out_dir, xp=None, perks=None):
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)          # drop stale categories (e.g. a renamed tree)
    out_dir.mkdir(parents=True)
    ids = []
    for tree in data['trees']:
        ids.append(tree['id'])
        cat_dir = out_dir / 'categories' / tree['id']      # Pufferfish reads config/puffish_skills/categories/<id>/
        cat_dir.mkdir(parents=True)
        for name, content in build_category(tree, data['tiers'], xp, perks).items():
            (cat_dir / name).write_text(json.dumps(content, indent=2) + '\n', encoding='utf-8')
    config = {'version': 3, 'show_warnings': True, 'categories': ids}
    (out_dir / 'config.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')


def main():
    data = json.loads((HERE / 'trees.json').read_text(encoding='utf-8'))
    write_config(data, OUT, load('xp.json'), load('perks.json') if (HERE / 'perks.json').exists() else None)
    print(f'wrote {len(data["trees"])} categories to {OUT}')


if __name__ == '__main__':
    main()
